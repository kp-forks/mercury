"""The public notebook listing must not accept a caller-selected filesystem root."""

import json
from pathlib import Path
import tempfile
from urllib.parse import urlencode

from jupyter_server.auth import PasswordIdentityProvider
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from mercury_app.notebooks import NotebooksAPIHandler


class TestNotebooksAPI(AsyncHTTPTestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="mercury-listing-test-")
        self.addCleanup(self.workspace.cleanup)
        self.parent = Path(self.workspace.name)
        self.served = self.parent / "served"
        self.outside = self.parent / "outside"
        self.write_notebook(self.served / "public.ipynb", "Public notebook")
        self.write_notebook(self.served / "nested" / "child.ipynb", "Served child")
        self.write_notebook(self.outside / "private.ipynb", "Private notebook")
        self.write_notebook(self.outside / "nested" / "private.ipynb", "Private child")
        super().setUp()

    @staticmethod
    def write_notebook(path, title):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "nbformat": 4,
                    "nbformat_minor": 5,
                    "cells": [],
                    "metadata": {
                        "mercury": {
                            "title": title,
                            "description": title + " description",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    def get_app(self):
        return Application(
            [(r"/prefix/mercury/api/notebooks", NotebooksAPIHandler)],
            # Real anonymous Jupyter auth, not a mocked authenticated user.
            identity_provider=PasswordIdentityProvider(token="", hashed_password=""),
            cookie_secret="test-only-cookie-secret",
            base_url="/prefix/",
            notebooks_dir=str(self.served),
            notebooks_recursive=False,
        )

    def listing(self, **query):
        response = self.fetch("/prefix/mercury/api/notebooks?" + urlencode(query))
        assert response.code == 200, response.body
        assert response.headers["Content-Type"].startswith("application/json")
        return json.loads(response.body)

    def test_anonymous_listing_preserves_metadata_and_base_url(self):
        items = self.listing()
        assert [item["name"] for item in items] == ["Public notebook"]
        assert items[0]["description"] == "Public notebook description"
        assert items[0]["href"] == "/prefix/mercury/public.ipynb"
        assert items[0]["slug"] == "/prefix/mercury/public"

    def test_directory_overrides_are_ignored(self):
        baseline = self.listing()
        for target in (
            str(self.outside),
            str(self.parent),
            "../outside",
            str(self.outside / "nested"),
            str(self.parent / "missing"),
            "C:\\Windows",
            "C:\\missing-test-directory",
            "",
        ):
            with self.subTest(target=target):
                assert self.listing(dir=target, recursive="1") == baseline

    def test_existing_and_missing_paths_do_not_form_an_oracle(self):
        assert self.listing(dir=str(self.outside)) == self.listing(
            dir=str(self.parent / "missing")
        )

    def test_query_cannot_enable_recursion(self):
        for value in ("1", "true", "True"):
            with self.subTest(value=value):
                assert [item["name"] for item in self.listing(recursive=value)] == [
                    "Public notebook"
                ]

    def test_configured_recursion_cannot_be_overridden(self):
        self._app.settings["notebooks_recursive"] = True
        for query in (
            {},
            {"recursive": "0"},
            {"dir": str(self.outside), "recursive": "false"},
        ):
            with self.subTest(query=query):
                assert {item["name"] for item in self.listing(**query)} == {
                    "Public notebook",
                    "Served child",
                }

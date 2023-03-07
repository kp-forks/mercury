# Generated by Django 3.2.5 on 2023-03-07 13:39

import apps.accounts.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadedFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("filename", models.CharField(max_length=1024)),
                ("filepath", models.CharField(max_length=1024)),
                ("filetype", models.CharField(max_length=128)),
                ("filesize", models.IntegerField()),
                (
                    "created_at",
                    apps.accounts.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "hosted_on",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="accounts.site"
                    ),
                ),
            ],
        ),
    ]

# Generated by Django 4.2.1 on 2023-06-20 12:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Machine",
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
                ("ipv4", models.CharField(blank=True, max_length=128)),
                ("state", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
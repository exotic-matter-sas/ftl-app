# Generated by Django 2.2.13 on 2020-07-22 11:19

import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_auto_20200428_1723"),
    ]

    operations = [
        migrations.CreateModel(
            name="FTLDocumentSharing",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "pid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
                ("edited", models.DateTimeField(auto_now=True)),
                ("expire_at", models.DateTimeField(blank=True, null=True)),
                ("password", models.CharField(blank=True, max_length=128, null=True)),
                ("note", models.TextField(blank=True)),
                (
                    "ftl_doc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="share_pids",
                        to="core.FTLDocument",
                    ),
                ),
            ],
            options={"ordering": ["-created"],},
        ),
    ]
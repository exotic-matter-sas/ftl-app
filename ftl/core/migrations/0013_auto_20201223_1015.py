# Generated by Django 2.2.16 on 2020-12-23 09:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_auto_20201211_1724"),
    ]

    operations = [
        migrations.CreateModel(
            name="FTLDocumentReminder",
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
                ("alert_on", models.DateTimeField()),
                ("note", models.TextField(blank=True)),
                (
                    "ftl_doc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reminders",
                        to="core.FTLDocument",
                    ),
                ),
                (
                    "ftl_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["alert_on"],},
        ),
        migrations.AddConstraint(
            model_name="ftldocumentreminder",
            constraint=models.UniqueConstraint(
                fields=("ftl_doc", "ftl_user", "alert_on"), name="one_alert_per_day"
            ),
        ),
    ]

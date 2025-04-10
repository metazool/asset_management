# Generated by Django 5.0.2 on 2025-04-10 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assets", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="calibrationcertificate",
            name="corrective_actions",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="calibrationcertificate",
            name="non_conformities",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

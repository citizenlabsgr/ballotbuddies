# Generated by Django 4.0.3 on 2022-04-09 01:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0010_voter_created"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="voter",
            options={"ordering": ["-created"]},
        ),
    ]

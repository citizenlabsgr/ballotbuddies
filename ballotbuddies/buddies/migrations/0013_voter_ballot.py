# Generated by Django 4.0.5 on 2022-06-27 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buddies", "0012_voter_absentee"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="ballot",
            field=models.URLField(blank=True, null=True),
        ),
    ]

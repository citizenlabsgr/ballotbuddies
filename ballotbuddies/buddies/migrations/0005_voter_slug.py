# Generated by Django 3.2.8 on 2021-10-21 23:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0004_voter_referrer"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="slug",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

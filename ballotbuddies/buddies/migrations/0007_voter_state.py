# Generated by Django 3.2.8 on 2021-10-24 03:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0006_voter_community"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="state",
            field=models.CharField(default="Michigan", editable=False, max_length=20),
        ),
    ]

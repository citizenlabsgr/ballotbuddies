# Generated by Django 4.2 on 2023-07-09 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buddies", "0017_alter_voter_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="fetched",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.0.3 on 2024-07-10 00:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0021_voter_ballot_updated"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="ballot_shared",
            field=models.DateTimeField(
                blank=True,
                help_text="Voter has shared their completed sample ballot.",
                null=True,
            ),
        ),
    ]

# Generated by Django 4.0.5 on 2022-06-29 20:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0014_alter_voter_ballot"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="nickname",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

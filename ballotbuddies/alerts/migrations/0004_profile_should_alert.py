# Generated by Django 4.0.5 on 2022-06-25 01:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alerts", "0003_alter_profile_voter"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="should_alert",
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.0.5 on 2022-07-16 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0012_profile_should_alert_computed"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="will_alert",
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
# Generated by Django 4.0.3 on 2022-04-09 00:34

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buddies", "0009_alter_voter_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]

# Generated by Django 3.2.8 on 2021-10-16 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buddies", "0001_voter"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voter",
            name="zip_code",
            field=models.CharField(max_length=5, null=True, verbose_name="ZIP code"),
        ),
    ]

# Generated by Django 3.2 on 2022-07-27 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0023_schedule__free_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='free_dates',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
# Generated by Django 3.2 on 2022-07-28 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0025_rename__free_dates_schedule__dates_listed'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='date_for',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]

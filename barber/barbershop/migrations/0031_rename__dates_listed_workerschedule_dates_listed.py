# Generated by Django 3.2 on 2022-08-03 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0030_rename_free_dates_workerschedule__dates_listed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workerschedule',
            old_name='_dates_listed',
            new_name='dates_listed',
        ),
    ]

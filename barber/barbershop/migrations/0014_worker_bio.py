# Generated by Django 3.2 on 2022-07-19 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0013_auto_20220720_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]
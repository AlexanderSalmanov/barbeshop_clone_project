# Generated by Django 3.2 on 2022-07-18 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0003_auto_20220719_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, unique=True),
        ),
    ]
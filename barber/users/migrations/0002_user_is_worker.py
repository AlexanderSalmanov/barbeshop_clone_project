# Generated by Django 3.2 on 2022-07-19 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_worker',
            field=models.BooleanField(default=False),
        ),
    ]
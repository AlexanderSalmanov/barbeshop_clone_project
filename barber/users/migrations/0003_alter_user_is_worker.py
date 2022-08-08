# Generated by Django 3.2 on 2022-07-31 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_is_worker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_worker',
            field=models.BooleanField(default=False, help_text='Determines if the user is a member of the company or just an ordinary client.'),
        ),
    ]
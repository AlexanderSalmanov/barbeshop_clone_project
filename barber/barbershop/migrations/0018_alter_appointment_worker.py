# Generated by Django 3.2 on 2022-07-23 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0017_auto_20220723_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='worker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='barbershop.worker'),
        ),
    ]

# Generated by Django 3.2 on 2022-07-19 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0008_auto_20220719_0117'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='total_duration',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

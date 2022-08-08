# Generated by Django 3.2 on 2022-08-02 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0028_auto_20220803_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='schedules',
            field=models.ManyToManyField(blank=True, null=True, through='barbershop.WorkerSchedule', to='barbershop.Schedule'),
        ),
        migrations.AlterField(
            model_name='workerschedule',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules_set', to='barbershop.worker'),
        ),
    ]

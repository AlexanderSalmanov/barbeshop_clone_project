# Generated by Django 3.2 on 2022-08-02 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('barbershop', '0027_alter_schedule_date_for'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worker',
            name='free_dates',
        ),
        migrations.RemoveField(
            model_name='worker',
            name='schedule',
        ),
        migrations.CreateModel(
            name='WorkerSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('free_dates', models.JSONField(blank=True, null=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workers', to='barbershop.schedule')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='barbershop.worker')),
            ],
        ),
    ]

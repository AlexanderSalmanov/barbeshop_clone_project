# Generated by Django 3.2 on 2022-07-18 20:36

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('SCISSORSHARICUT', 'Scissors haircut'), ('CLIPPERHAIRCUT', 'Clipper Haircut'), ('BEARDCUT', 'Beard Cut'), ('STYLING', 'Styling'), ('BROWCORRECTION', 'Brow Correction'), ('COMBINEDCUT', 'Combined Haircut')], max_length=100)),
                ('price', models.PositiveIntegerField(default=100)),
                ('estimated_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worker_name', models.CharField(max_length=100)),
                ('slug', models.SlugField(allow_unicode=True, unique=True)),
                ('rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)])),
                ('expertise', models.CharField(choices=[('MENS', "Men's cuts"), ('WOMENS', "Women's cuts"), ('SHAVING', 'Shaving'), ('KIDS', "Kids' cuts")], max_length=100)),
                ('working_dates', models.CharField(default='blank', max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_visited', models.PositiveIntegerField(default=0)),
                ('birthday', models.DateTimeField(default=None)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True)),
                ('end_time', models.DateTimeField(blank=True)),
                ('total_price', models.PositiveIntegerField(default=0.0)),
                ('is_done', models.BooleanField(default=False)),
                ('client', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='barbershop.client')),
                ('services', models.ManyToManyField(to='barbershop.Service')),
                ('worker', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='barbershop.worker')),
            ],
        ),
    ]

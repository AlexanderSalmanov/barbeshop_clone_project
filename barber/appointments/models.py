from django.db import models
from django.db.models.signals import m2m_changed, pre_delete, pre_save
from django.urls import reverse

from barbershop.models import Service, Worker, WorkerSchedule
from datetime import datetime, date, timedelta

import json
# Create your models here.

class Appointment(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    client_email = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    services = models.ManyToManyField(Service, related_name='services', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True) # datetime.time
    end_time = models.DateTimeField(blank=True, null=True) #datetime.time + sum([i.estimated_time for i in self.servies.all()])
    total_price = models.PositiveIntegerField(default=0.0)
    total_duration = models.CharField(max_length=100, blank=True, null=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_client_name}'s {self.services.first().title} on {self.start_time}"

    @property
    def get_client_name(self):
        if self.client_name:
            return self.client_name
        return self.client_email

    def get_delete_url(self):
        return reverse('appointments:delete_appointment', kwargs={'id':self.id})

    def _mark_done(self):
        self.is_done = True
        self.save()

def m2m_changed_price_counter(sender, instance, action, *args, **kwargs):
    '''
    m2m_changed signal designed to automate the price counting
    '''
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        total = sum([int(i.price) for i in instance.services.all()])
        instance.total_price = total
        instance.save()

m2m_changed.connect(m2m_changed_price_counter, sender=Appointment.services.through)

def restore_date_on_delete(sender, instance, *args, **kwargs):
    '''
    pre_delete signal which inserts Appointment's start date back
    to barber's schedule when the Appointment is cancelled (deleted)
    for some reason.
    '''
    if instance.start_time:
        app_start_date = date(
            year=instance.start_time.year,
            month=instance.start_time.month,
            day=instance.start_time.day
        )
        ws_obj = WorkerSchedule.objects.get(
            worker=instance.worker,
            schedule__date_for=app_start_date
        )
        free_dates = ws_obj.get_free_dates()
        free_dates.append(datetime.strftime(instance.start_time, '%Y-%m-%d, %H:%M'))
        free_dates.sort()
        ws_obj.dates_listed = json.dumps(free_dates)
        ws_obj.save()

pre_delete.connect(restore_date_on_delete, sender=Appointment)

def appointment_address_filler(sender, instance, *args, **kwargs):
    '''
    Simple signal for filling Appointment model 'address' field. To remove
    redundant manipulations, this signal just extracts 'address' field value
    from Location model related to Worker instance, and then it pastes it
    directly to Appointment's 'address' field.
    '''
    if instance.worker.location:
        instance.address = instance.worker.location.address

pre_save.connect(appointment_address_filler, sender=Appointment)

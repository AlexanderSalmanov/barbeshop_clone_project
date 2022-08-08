from django.contrib import admin
from .models import Appointment
# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client_email', 'worker', 'start_time']
    list_filter = ['client_email', 'worker']

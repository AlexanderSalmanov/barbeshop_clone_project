from django.contrib import admin

from django_google_maps import fields as map_fields
from django_google_maps import widgets as map_widgets

from .models import Worker, Service, Schedule, Location, WorkerSchedule
# Register your models here.
admin.site.register(Worker)
admin.site.register(Service)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {
            'widget': map_widgets.GoogleMapsAddressWidget(attrs={'data-map-type': 'hybrid'})
        }
    }

@admin.register(WorkerSchedule)
class WorkerScheduleAdmin(admin.ModelAdmin):
    list_display = ['worker', 'schedule']
    list_filter = ['worker']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_filter = ['title']

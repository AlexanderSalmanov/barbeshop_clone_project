from django.urls import path
from . import staff_views
from . import admin_views

app_name = 'staff'

urlpatterns = [
    path('my-appointments/', staff_views.worker_pending_appointments, name='worker_appointments'),
    path('mark-done/<int:item_id>/', staff_views.mark_appointment_done, name='mark_done'),
    path('set-schedule/', staff_views.set_weekly_schedule, name='set_weekly_schedule'),
    path('appointments-on/<str:date>/', staff_views.date_filtered_appointments, name='date_filter'),
    path('new-schedules/', admin_views.create_schedules, name='create_schedules'),
    path('refresh-schedules/', admin_views.refresh_schedules, name='refresh_schedules'),
]

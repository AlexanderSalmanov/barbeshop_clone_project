from django.urls import path

from . import views

app_name = 'appointments'

urlpatterns = [
    path('select-location/', views.select_location, name='select_location'),
    path('select-barber/', views.select_barber, name='select_barber'),
    path('select-date/', views.select_date, name='select_date'),
    path('select-time/', views.select_time, name='select_time'),
    path('select-service/', views.select_service, name='select_service'),
    path('new/', views.create_appointment, name='create_appointment'),
    path('my/', views.client_appointments, name='client_appointments'),
    path('<int:id>/delete/', views.delete_appointment, name='delete_appointment')
]

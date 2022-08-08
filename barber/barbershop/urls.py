from django.urls import path

from . import views

app_name = 'barbershop'

urlpatterns = [
    path('services/', views.service_list, name='services'),
    path('team/', views.team_view, name='team'),
    path('about/<slug:slug>/', views.barber_info, name='barber_info'),
    path('<slug:slug>/', views.expertise_search, name='filters')
]

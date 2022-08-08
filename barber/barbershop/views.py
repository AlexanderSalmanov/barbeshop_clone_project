from django.shortcuts import render, redirect, get_object_or_404

from .models import Service, Worker

# Create your views here.

def service_list(request):
    '''
    Service list view.
    '''
    service_list = Service.objects.all()
    context = {
        'service_list': service_list
    }
    return render(request, 'barbershop/services.html', context)


def team_view(request):
    '''
    Worker list view. Front-end side also allows to filter barbers based off of
    their expertise.
    '''
    workers = Worker.objects.all()
    context = {
        'workers': workers
    }
    return render(request, 'barbershop/team.html', context)


def barber_info(request, slug):
    '''
    Barber detail view.
    '''
    worker_obj = get_object_or_404(Worker, slug=slug)
    worker_schedules = worker_obj.schedules_set.all()
    context = {
        'worker': worker_obj,
        'schedules': worker_schedules
    }
    return render(request, 'barbershop/barber_info.html', context)

def expertise_search(request, slug):
    '''
    View showing barbers with a selected expertise.
    '''
    service = get_object_or_404(Service, slug=slug)
    context = {
        'workers': [item for item in Worker.objects.all() if service in item.expertise.all()],
        'query': service.get_title_display(),
        'service_slug': service.slug
    }
    return render(request, 'barbershop/barbers_search.html', context)

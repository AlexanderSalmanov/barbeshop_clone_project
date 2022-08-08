from .models import Worker, Service, Location

def services(request):
    return {
        'services': Service.objects.all()
    }

def workers(request):
    return {
        'workers': Worker.objects.all()
    }

def locations(request):
    return {
        'locations': Location.objects.all()
    }

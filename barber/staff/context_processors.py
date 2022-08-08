from appointments.models import Appointment
from barbershop.models import Worker

from datetime import datetime, timedelta, date

def all_workers_appointment_dates(request):
    if not request.user.is_authenticated:
        return {}
    elif not request.user.is_worker:
        return {}
    worker_obj = Worker.objects.get(user=request.user)
    if worker_obj.appointment_set.all().count():
        appointments = worker_obj.appointment_set.all().order_by('-start_time')
        appointment_dates = [datetime.strftime(item.start_time, '%Y-%m-%d') for item in appointments]
        appointment_datetimes = [datetime.strftime(item.start_time, '%Y-%m-%d, %H:%S') for item in appointments]
        return {
            'appointment_dates': appointment_dates,
            'appointment_datetimes': appointment_datetimes
        }
    return {}

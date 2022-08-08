from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.db import IntegrityError

from barbershop.models import Worker, WorkerSchedule, Schedule
from appointments.models import Appointment

from datetime import datetime, timedelta, date

# Create your views here.

@login_required
def worker_pending_appointments(request):
    user = request.user
    if not user.is_worker:
        return HttpResponse('Sorry, this page is only for staff to be seen.')
    else:

        worker_obj = Worker.objects.get(user=user)
        appointments = worker_obj.appointment_set.all().order_by('-start_time')

        context = {
            'appointments': appointments,
        }
        return render(request, 'staff/worker_pending_appointments.html', context)

@login_required
def date_filtered_appointments(request, date):
    worker_obj = Worker.objects.get(user=request.user)
    date_formatted = datetime.strptime(date, '%Y-%m-%d')
    appointments = Appointment.objects.filter(
        worker=worker_obj,
        start_time__year=date_formatted.year,
        start_time__month=date_formatted.month,
        start_time__day=date_formatted.day
    )

    context = {
        'appointments': appointments,
        'chosen_date': date
    }
    return render(request, 'staff/worker_pending_appointments.html', context)

@login_required
def mark_appointment_done(request, item_id):
    appointment_item = get_object_or_404(Appointment, id=item_id)
    appointment_item._mark_done()
    return redirect('staff:worker_appointments')


@login_required
def set_weekly_schedule(request):
    if not request.user.is_worker:
        return HttpResponse('Sorry, you are not eligible for this action.')
    worker_obj = Worker.objects.get(user=request.user)
    sched_type = request.POST.get('daytimeChoice')
    print(sched_type)
    schedules_qs = Schedule.objects.filter(
        title=sched_type,
        date_for__lte=timezone.now() + timedelta(days=7),
        date_for__gte=timezone.now())
    try:
        ws_qs = WorkerSchedule.objects.bulk_create([
            WorkerSchedule(
                worker=worker_obj,
                schedule=entry
            ) for entry in schedules_qs
        ])
    # for item in ws_qs:
    #     worker_obj.schedules.add(item)
    except IntegrityError:
        messages.success(request, f'Your schedule for a week has been set.')
    return redirect('/')

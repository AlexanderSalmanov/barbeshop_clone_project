from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib import messages

from barbershop.models import Schedule, WorkerSchedule

from datetime import datetime, date, timedelta

@login_required
def create_schedules(request):
    '''
    Admin view designed to bulk_create new Schedule objects instead of manually
    creating them in the admin panel.
    '''
    if not request.user.is_admin:
        return HttpResponse('Sorry, this action is available only for admin users.')
    now = timezone.now()
    now_date = now.replace(year=now.year, month=now.month, day=now.day)
    week = [now_date + timedelta(days=i) for i in range(7)]
    sched_type = request.POST.get('schedType')
    try:
        if sched_type == 'D':
            Schedule.objects.bulk_create(
                    [Schedule(title=sched_type,
                              start_time='9:00',
                              end_time='15:00',
                              date_for=i) for i in week]
                )
        elif sched_type == 'E':
            Schedule.objects.bulk_create(
                    [Schedule(title=sched_type,
                              start_time='15:00',
                              end_time='21:00',
                              date_for=i) for i in week]
                )
    except IntegrityError:
        messages.success(request, f'New {sched_type}-typed schedules created successfully. Check admin panel for more detail.')
        return redirect('/')

@login_required
def refresh_schedules(request):
    '''
    Admin view designed to bulk_update all Schedules's date_for fields
    to make them correspond with the current day and not store Schedules
    related to past days.
    '''
    if not request.user.is_admin:
        return HttpResponse('Sorry, this action is available only for admin users.')
    now = timezone.now()
    now_date = now.replace(year=now.year, month=now.month, day=now.day)
    week = [now_date + timedelta(days=i) for i in range(7)]
    schedules_qs = Schedule.objects.all()
    schedule_before_dates = [i.date_for for i in schedules_qs]
    update_list = []
    buff = -1
    for key, value in enumerate(schedules_qs):

        week_key = key if key <= 6 else 0

        if key > 6:
            buff += 1
            if buff > 6:
                buff = 0
            week_key = buff

        value.date_for = week[week_key]
        if value.date_for not in schedule_before_dates:
            update_list.append(value)
    Schedule.objects.bulk_update(update_list, ['date_for'])
    for item in Schedule.objects.all():
        # if item.date_for not in schedule_before_dates:
        item.set_dates_listed()

    for item in WorkerSchedule.objects.all():
        if item.schedule.date_for not in schedule_before_dates:
            item.set_free_dates()

    messages.success(request, 'Schedules successfully updated.')
    return redirect('/')

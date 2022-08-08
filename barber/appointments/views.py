from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.contrib import messages

from barbershop.models import Worker, Service, WorkerSchedule, Location
from .models import Appointment
from .tasks import send_success_email_task

from datetime import datetime, timedelta, date
import json
import inspect
from copy import deepcopy
# Create your views here.


'''
The following section, starting with select_location and ending with
create_appointment, is a series of views which, in combination, allow the client
to book an appointment to the barbershop. One view = one stage of this process.
Each view will be shortly described below.

'''


def select_location(request):
    '''
    Simple view which extracts user's input in the form and performs following
    operations:
        1. Retrieve Location instance with a given ID;
        2. Get all Worker objects related to this location.
        3. Save the selected location address to a session variable to be
        retrieved soon at the final stage of this whole process.
    '''
    loc = request.POST.get('locationSelect')  # passing an ID
    loc_obj = Location.objects.get(id=loc)
    workers = [item.worker_name for item in loc_obj.workers]
    request.session['selected_location'] = loc_obj.address
    if request.is_ajax:
        json = {
            'location': loc_obj.address,
            'workers': workers
        }
        return JsonResponse(json)

def select_barber(request):
    '''
    Simple view which extracts user's input in the form and performs following
    operations:
        1. Retrieve Worker instance with a given worker_name;
        2. Save worker_obj's slug to a session variable (slugs are
        selected to remove duplicates and conflicts between various instances
        with possible identical worker_names);
        3. Extract all WorkerSchedule objects from the worker_obj (simply
        speaking: getting all available dates for a patricular barber);
        4. Extract dates from WorkerSchedule queryset (to be sent to the
        front-end).
    '''
    worker_name = request.POST.get('barberSelect')
    worker_obj = Worker.objects.get(worker_name=worker_name)
    request.session['selected_worker'] = worker_obj.slug
    ws_qs = WorkerSchedule.objects.filter(
        worker=worker_obj
    )
    worker_dates = [i.schedule.date_for for i in ws_qs]
    if request.is_ajax:
        json = {
            'worker_name': worker_name,
            'worker_dates': worker_dates,
        }
        return JsonResponse(json)


def select_date(request):
    '''
    Simple view which extracts user's input in the form and performs following
    operations:
        1. Get the worker_obj based on previous inputs;
        2. Get the selected_date from request.POST and cast it to a datetime
        format;
        3. Get WorkerSchedule instance related to previously selected barber
        and to the date selected by the user;
        4. Get free_dates variable by calling WorkerSchedule instance method;
        5. Extract only hours from free_dates to send them to the front-end for
        the next view;
        6. Save user's selected date to a session variable (both in string and
        datetime types).
    '''
    worker_slug = request.session.get('selected_worker')
    if worker_slug:
        worker_obj = Worker.objects.get(slug=worker_slug)

    selected_date = request.POST.get('dateInput')
    date_formatted = datetime.strptime(selected_date, '%Y-%m-%d')
    date_formatted = date(year=date_formatted.year, month=date_formatted.month, day=date_formatted.day)
    workers_schedule = WorkerSchedule.objects.get(schedule__date_for=date_formatted, worker=worker_obj)

    free_dates = workers_schedule.get_free_dates()
    free_hours = [item.split(',')[1][1:] for item in free_dates]
    request.session['date_formatted'] = str(date_formatted)
    request.session['selected_date'] = selected_date
    if request.is_ajax:
        json = {
            'selected_date': selected_date,
            'free_hours': free_hours
        }
        return JsonResponse(json)


def select_time(request):
    '''
    Simple view which extracts user's input in the form and performs following
    operations:
        1. Get the worker_obj from previous user's inputs.
        2. Get the expertise (more simply - all service which may be done
        by the barber);
        3. Get selected_date from the session;
        4. Get selected_time from request.POST data;
        5. Combine selected_date and selected_time using the f-string (to get
        a fully-fledged datetime necessary for WorkerSchedule's free_dates
        field);
        6. Save selected_time and result_time to the session.
        7. Save service_titles and barber_expertise to the JSON response
        for the front-end of the next view. It's done to limit the user to
        select only those services which are present in the selected barber's
        expertise.
    '''
    worker_slug = request.session.get('selected_worker')
    if worker_slug:
        worker_obj = Worker.objects.get(slug=worker_slug)
        expertise = worker_obj.expertise.all()
    selected_date = request.session.get('selected_date')
    selected_time = request.POST.get('timeInput')
    result_time = f"{selected_date}, {selected_time}"
    request.session['selected_time'] = selected_time
    request.session['result_time'] = result_time
    if request.is_ajax:
        json = {
            'selected_barber': worker_obj.worker_name,
            'result_time': result_time,
            'service_titles': [item.get_title_display() for item in expertise],
            'barber_expertise': [item.title for item in expertise]
        }
        return JsonResponse(json)


def select_service(request):
    '''
    Simple view which extracts user's input in the form and performs following
    operations:
        1. Get worker_obj, result_time (f-string with datetime of an appointment)
        from the session;
        2. Get the list of selected services from request.POST data
            IMPORTANT:
                It can't be done by using request.POST.get method because it
                only returns one value from the list. request.POST.getlist is
                used instead.
        3. Get the Service queryset which contains all services selected by
        the user;
        4. Get service_titles to display them on the front-end side of the
        final appointment booking form.
        5. Save list of selected services to the session.
    '''
    worker_slug = request.session.get('selected_worker')
    worker_obj = get_object_or_404(Worker, slug=worker_slug)
    result_time = request.session.get('result_time')

    selected_service = request.POST.getlist('serviceInput')

    services_qs = Service.objects.filter(
        title__in=selected_service
    )
    service_titles = [i.get_title_display() for i in services_qs]
    request.session['selected_service'] = selected_service
    if request.is_ajax:
        json = {
            'worker_name': worker_obj.worker_name,
            'result_time': result_time,
            'service_titles': [i.get_title_display() for i in services_qs],
            'service_price': sum(item.price for item in services_qs),
            'address': worker_obj.location.address
        }
        return JsonResponse(json)

def create_appointment(request):
    '''
    Final stage of appointment booking process. This view is a bit more complex,
    so some detail step-by-step:
        1. Get email_address and client_name inputs from the form (these
        fields are required for an Appointment instance);
        2. Get worker_obj and ws_qs (WorkerSchedule queryset). ws_qs is related
        to worker_obj and to the previously selected datetime, which is extracted
        from the request.session variable. Hours and minutes are removed from
        request.session.get('date_formatted') because WorkerSchedule's date_for
        field is a DATE, not a DATETIME.
        ---- next steps will be described right under corresponding pieces of
        code for better readability ----

    '''
    email_address = request.POST.get('emailInput')
    client_name = request.POST.get('nameInput')

    worker_slug = request.session.get('selected_worker')
    worker_obj = Worker.objects.get(slug=worker_slug)
    ws_obj = WorkerSchedule.objects.get(
        worker=worker_obj,
        schedule__date_for=datetime.strptime(request.session.get('date_formatted'), '%Y-%m-%d')
    )

    if email_address and client_name:
        '''
        3. If email and name inputs are not blank, we create a new Appointment
        instance, with only required fields for now;
        '''
        app_obj = Appointment.objects.create(
            worker=worker_obj,
            client_email=email_address,
            client_name=client_name
        )

        '''
        4. Get selected_service list from the session, and get the Service
        queryset based on that list.
        5. One by one, we add each item from the services_qs to the m2m relationship
        between our newly created Appointment and Service.
        '''
        selected_service = request.session.get('selected_service')
        services_qs = Service.objects.filter(
            title__in=selected_service
        )
        for item in services_qs:
            app_obj.services.add(item)


        '''
        6. Get the result_time from the session, cast it to a datetime format,
        and assign the result to the Appointment instance's start_time field.
        7. Use list comprehension to extract all durations from services_qs and
        split them on the colon to cast separate digits to integers;
        8. Utilizing timedelta to gradually increment app_obj.start_time by
        the duration of every single selected service, and assigning the result
        to app_obj.end_time field.
        9. Updating worker's free dates by utilizing WorkerSchedule's update_free_dates
        method. Check this method's docs in barbershop/models.py for more detail.
        '''
        app_obj.start_time = datetime.strptime(request.session.get('result_time'), '%Y-%m-%d, %H:%M')
        service_durations = [i.duration.split(':') for i in services_qs]
        end_date = app_obj.start_time
        for item in service_durations:
            end_date += timedelta(hours=int(item[0]), minutes=int(item[1]))
        ws_obj.update_free_dates(app_obj.start_time, end_date)

        app_obj.end_time = end_date

        app_obj.save()

        """
        10. If the user agrees to receive a confirmation email, delegate the
        send email task to Celery
        """
        if request.POST.get('sendEmail'):

            send_success_email_task.delay(
                client_email=email_address,
                worker_name=worker_obj.worker_name,
                start_date=datetime.strftime(app_obj.start_time, '%Y-%m-%d, %H:%M'),
                service=services_qs.first().get_title_display(),
                duration=service_obj.duration,
                price=service_obj.price
            )
        '''
        11. As long as appointment booking functionality is available for
        non-logged in users, anonymous users are identified by the email they
        gave in the client_email variable. This variable is saved to the session
        and it's not deleted in the final session cleanup.
        '''
        if not request.user.is_authenticated:
            request.session['guest_email'] = email_address
            #

        '''
        12. Finally, deleting all session variables related to appointment booking
        to escape collisions between previous and future inputs.
        '''
        del request.session['date_formatted']
        del request.session['selected_date']
        del request.session['selected_time']
        del request.session['result_time']
        del request.session['selected_service']
        del request.session['selected_worker']
    messages.success(request, f'You have successfully appointed to {worker_obj.worker_name} at {app_obj.start_time}.')
    return redirect('appointments:client_appointments')


def client_appointments(request):
    '''
    View which shows all appointments booked by the current user.
    If the user is anonymous, then he is identified by
    request.session.get('guest_email'), which is NOT deleted after submitting
    the final appointment booking form.
    In the opposite case, things are much more simple, and all appointments
    are filteted by the current user's email.
    '''
    if not request.user.is_authenticated:
        appointments = Appointment.objects.filter(client_email=request.session.get('guest_email'))
    else:
        appointments = Appointment.objects.filter(client_email=request.user.email)
    context = {
        'appointments': appointments
    }
    return render(request, 'barbershop/client_appointments.html', context=context)

def delete_appointment(request, id):
    '''
    I guess, these three lines of code don't even need a docstring to them.
    '''
    app_obj = get_object_or_404(Appointment, id=id)
    app_obj.delete()
    return redirect('appointments:client_appointments')

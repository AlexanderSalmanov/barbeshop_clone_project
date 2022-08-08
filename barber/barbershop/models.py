from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django_google_maps import fields as map_fields

from barber.managers import CustomBulkManager

from .utils import suffix_generator
from . import choices

from datetime import datetime, timedelta, date
import json

# Create your models here.

User = settings.AUTH_USER_MODEL


"""
------------------------
Worker model and signals
------------------------
"""
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    worker_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    rating = models.DecimalField(default=0.0, decimal_places=2, max_digits=3, validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])
    profile_pic = models.ImageField(upload_to='barbershop/workers/profile_pics/', blank=True, null=True)
    expertise = models.ManyToManyField('Service', related_name='expertise', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    schedules = models.ManyToManyField('Schedule', blank=True, null=True, through='WorkerSchedule')
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, default=1)

    def __str__(self):
        return self.worker_name

    def get_absolute_url(self):
        return reverse('barbershop:barber_info', kwargs={'slug': self.slug})



def post_save_worker_name_filler(sender, instance, created, *args, **kwargs):
    '''
    Post_save signal which fills in Worker's worker_name field by extracting
    the attached User's full_name field.
    This signal is triggered once the User with a corresponding permission
    (is_worker = True) is registered.
    '''
    if created and instance.is_worker:
        worker_name = instance.full_name
        Worker.objects.get_or_create(user=instance, worker_name=worker_name)

post_save.connect(post_save_worker_name_filler, sender=User)

def post_save_unique_slug(sender, instance, created, *args,  **kwargs):
    '''
    Simple signal for adding a unique prefix to each worker's slug field
    to ensure that it's unique.
    '''
    if created:
        slug = instance.slug
        qs = Worker.objects.filter(slug=slug)
        if qs.count() >= 1:
            instance.slug = suffix_generator(slug)
            instance.save()

post_save.connect(post_save_unique_slug, sender=Worker)

"""
-----------------------
Schedule model and stuff
-----------------------
"""

class Schedule(models.Model):
    TITLE_CHOICES = (
        ('D', 'Day'),
        ('E', 'Evening')
    )
    title = models.CharField(max_length=2, choices=TITLE_CHOICES, blank=True, null=True)
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)
    date_for = models.DateField(default=timezone.now)
    dates_listed = models.JSONField(blank=True, null=True)

    objects = CustomBulkManager()

    def __str__(self):
        return f"{self.title}, {self.date_for}; ID: {self.id}"


    def set_dates_listed(self):
        '''
        Model method for filling dates_listed field.
        This field is designated for keeping all separate dates available
        for clients for appointment booking.
        1. Take start and end hours from start_time and end_time str fields.
        2. Create start_date variable by combining model's date_for field date
        properties and adding time properties received one step above.
        3. Fill the dates list by entries with a 1 hour 30 minute (1:30) gap.
        4. For future convenience, this method both modifies the model's field
        and returns its generated value.
        '''
        dates = []
        start_hour = int(self.start_time.split(':')[0])
        end_hour = int(self.end_time.split(':')[0])
        start_date = datetime(
            year=self.date_for.year,
            month=self.date_for.month,
            day=self.date_for.day,
            hour=start_hour,
            minute=0,
            second=0)
        dates.append(datetime.strftime(start_date, '%Y-%m-%d, %H:%M')) # Filling the first entry
        while start_hour < end_hour:
            # if timezone.now() > start_date:
            #     start_date += timedelta(days=1)
            start_date += timedelta(hours=1, minutes=30)
            start_hour = start_date.hour
            dates.append(datetime.strftime(start_date, '%Y-%m-%d, %H:%M'))
        dates = list(set(dates))
        dates.sort()
        dates = json.dumps(dates[:-1])
        self.dates_listed = dates
        self.save()
        return dates

    def get_dates_listed(self):
        '''
        Getter method which retrieves model's dates_listed JSON field, casts
        it to a list, and returns an identical list value.
        '''
        listed_dates = list(set(json.loads(self.dates_listed)))
        return listed_dates


def schedule_dates_filler(sender, instance, created, *args, **kwargs):
    '''
    Post_save signal which automatically fills in schedule's dates_listed field
    each time a new Schedule object is created.
    '''
    if created:
        dates_listed = instance.set_dates_listed()
        instance.dates_listed = dates_listed
        instance.save()


post_save.connect(schedule_dates_filler, sender=Schedule, dispatch_uid='barbershop.models')

"""
-----------------------
WorkerSchedule model and stuff
-----------------------
"""

class WorkerSchedule(models.Model):
    worker = models.ForeignKey('Worker', on_delete=models.CASCADE, related_name='schedules_set')
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='workers')
    dates_listed = models.JSONField(blank=True, null=True)

    objects = CustomBulkManager()

    def __str__(self):
        return f'{self.worker.worker_name}\'s schedule for {self.schedule.date_for}'

    def get_free_dates(self):
        '''
        Getter method which is fully identical to Schedule's get_dates_listed().
        '''
        free_dates_list = json.loads(self.dates_listed)
        return free_dates_list

    def set_free_dates(self):
        '''
        Setter method which is fully identical to Schedule's set_dates_listed().
        '''
        schedule_obj = self.schedule # retrieve object
        self.dates_listed = schedule_obj.set_dates_listed() # call set_dates_listed() off that object to populate model field
        self.save()

    @property
    def free_hours(self):
        '''
        Model property which extracts hours from model's free_dates field.
        '''
        dates = self.get_free_dates()
        hours_only = [item.split(',')[1][1:] for item in dates]
        return hours_only


    def update_free_dates(self, app_start_date, app_end_date):
        '''
        Model method for updating worker's free_dates when the client is
        appointed to some service with a certain duration.
        1. Retrieve self's free_dates variable via getter method.
        2. Cast app_start_date and app_end_date arguments to string.
        3. Assign the position of appointment's start date in free_dates list
        to the start_idx variable.
        4. Pop it from the free_dates list.
        5. Create a timedelta-typed duration_timedelta variable, which is then
        used to check if the services selected by a client last longer than
        1:30 in total.
        6. After this check, dates list gets dumped to a JSON formated, attached
        to self's dates_listed field, and the model instance is saved. 
        '''
        dates = self.get_free_dates()
        start_date_str = datetime.strftime(app_start_date, '%Y-%m-%d, %H:%M')
        end_date_str = datetime.strftime(app_end_date, '%Y-%m-%d, %H:%M')
        start_idx = dates.index(start_date_str)
        dates.pop(start_idx)
        duration_timedelta = timedelta(
            hours=app_end_date.hour-app_start_date.hour,
            minutes=app_end_date.minute-app_start_date.minute
        )
        if duration_timedelta > timedelta(hours=1, minutes=30):
            '''
            Additional behaviour for cases when the services booked by a client
            last longer than 1:30 in total, so that free_dates list should be updated a
            bit more specifically.
            '''
            next_idx = start_idx + 1
            dates.insert(next_idx, end_date_str)
            dates.pop(start_idx)

            dates[:start_idx].extend(dates[next_idx:])


            if next_idx == len(dates) - 1:          #checking if the next date is not the last
                dates.pop(len(dates)-1)             # popping off the last element in the list
        self.dates_listed = json.dumps(dates)
        self.save()


def ws_date_filler(sender, instance, created, *args, **kwargs):
    '''
    Post_save signal which is fully identical to Schedule's dates filler which
    was implemented above.
    '''
    if created:
        instance.dates_listed = instance.schedule.set_dates_listed()
        instance.save()

post_save.connect(ws_date_filler, sender=WorkerSchedule)


"""
-----------------------
Service model and stuff
-----------------------
"""
class Service(models.Model):
    title = models.CharField(max_length=100, choices=choices.SERVICE_CHOICES)
    slug = models.SlugField(blank=True, null=True)
    price = models.PositiveIntegerField(default=100)
    duration = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(default='No description provided.')

    def save(self, *args, **kwargs):
        '''
        Simple solution implemented for automatical slug generation once
        the model instance is saved.
        '''
        slug = slugify(self.get_title_display())
        self.slug = slug
        return super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

"""
-----------------------
Location model and stuff
-----------------------
"""

class Location(models.Model):
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=100, default='50,50')

    def __str__(self):
        return str(self.address)

    @property
    def workers(self):
        if self.worker_set.all().count():
            return self.worker_set.all()

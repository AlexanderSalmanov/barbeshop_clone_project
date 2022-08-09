### This is my project where I'm trying to implement all features which are crucial for a barbershop: appointment booking, proper date handling and so on.
The project still needs some bug fixes related to date and workers' schedule handling to make the entire process of managing barbers' working time simple and transparent.

##### This project can be divided into 3 sections for the following user types:
  
  - Ordinary users (clients of the barbershop)
  - Staff users (barbers, workers of the organization)
  - Admin users
  
  
##### Clients are allowed to do the following:
  
  - Check all organization's barbers and filter them out based on the services they are able to provide;
  - Book an appointment to the barbershop for a specific time for a multiple services;
  - Receive confirmation Emails once they have booked an appointment;
  - See all their pending appointments.

##### Barbers can do the following:
  - Assign themselves a schedule for a week in advance (schedules also have specific type: Day or Evening);
  - See a list of all their pending appointments and filter them by date;

##### Admins can do the following:
  - Manage barbers' schedules: create new ones or update the old ones (directly with the site's UI not the admin panel)

### How do I setup and run this project?
  1. Download the zip-file with the project files;
  2. Create a virtual environment with the command ```python -m venv env```;
  3. Activate the virtual environment: ```env/scripts/activate```;
  4. Install all necessary packages by running the command ```pip install -r requirements.txt```;
  5. Run all the migrations to create a db.sqlite3 file: ```python manage.py migrate```;
  6. Create an admin user with the command ```python manage.py createsuperuser``` and fill in the credentials as you wish;
  7. To run the local server, type in the command ```python manage.py runserver```;
  8. To run the Celery worker, type in ```celery -A barber worker --loglevel=info --pool=solo```;
  9. Go to the site and register various user types to fully test the project's functionality!

  
  

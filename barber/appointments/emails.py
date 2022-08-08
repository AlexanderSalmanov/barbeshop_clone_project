from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage

def send_success_email(client_email, worker_name, start_date, service, duration, price):

    context = {
        'client_email': client_email,
        'worker_name': worker_name,
        'start_date': start_date,
        'service': service,
        'duration': duration,
        'price': price
    }

    email_subject = "You have successfully appointed to us!"
    email_body = render_to_string('email_message.txt', context)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [client_email, ]
    )
    return email.send(fail_silently=False)

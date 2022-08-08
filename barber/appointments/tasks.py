from celery.utils.log import get_task_logger
from celery import shared_task

from .emails import send_success_email

logger = get_task_logger(__name__)

@shared_task(bind=True)
def send_success_email_task(self, client_email, worker_name, start_date, service, duration, price):
    '''
    Celery task for sending emails to clients once they fill in the last
    appointment booking form.
    IMPORTANT:
        This task is only called if the user ticks the checkbox in the last form.
    '''
    logger.info('Sent success email.')
    return send_success_email(client_email, worker_name, start_date, service, duration, price)

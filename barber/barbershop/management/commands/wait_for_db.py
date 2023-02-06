import time 

from psycopg2 import OperationalError as Psycopg2OperError 

from django.db.utils import OperationalError 
from django.core.management.base import BaseCommand 


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting for db...")
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OperError, OperationalError):
                self.stdout.write("Waiting for 1 second...")
                time.sleep(1)
                
        self.stdout.write(self.style.SUCCESS("Database ready!"))
        
    
        
            
     
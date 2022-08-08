from django.db import models
from django.db.models.signals import post_save


class CustomBulkManager(models.Manager):

    def bulk_create(self, objs, **kwargs):
        for entry in objs:
            post_save.send(sender=entry.__class__, instance=entry, created=True, dispatch_uid='barber.managers')
            entry.save()
            if not entry.dates_listed:
                entry.delete()
        return super(CustomBulkManager, self).bulk_create(objs, **kwargs)

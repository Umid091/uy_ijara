from django.db.models.signals import post_save
from django.dispatch import receiver
from houses.models import Report, House


@receiver(post_save, sender=Report)
def broker_auto_block(sender, instance, created, **kwargs):
    if not created:
        return

    target_user = instance.reported_user
    if target_user.received_reports.count() >= 5 and not target_user.is_blocked:
        target_user.is_blocked = True
        target_user.save(update_fields=['is_blocked'])
        House.objects.filter(owner=target_user).delete()

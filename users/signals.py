from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User  # User o'zining modellaridan olinadi
from houses.models import Report, House  # Report va House boshqa app'dan olinadi


@receiver(post_save, sender=Report)
def broker_auto_block(sender, instance, created, **kwargs):
    if created:
        target_user = instance.reported_user
        target_user.report_count += 1
        target_user.save()

        if target_user.report_count >= 5:
            # Foydalanuvchini bloklash
            target_user.is_active = False
            target_user.save()

            # Uylarini o'chirish
            House.objects.filter(owner=target_user).delete()
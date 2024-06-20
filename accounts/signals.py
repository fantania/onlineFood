from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile

@receiver(post_save, sender=User) #The action= in the following method which is the receiver, when= post_save, who willl send the signal+ User 
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)
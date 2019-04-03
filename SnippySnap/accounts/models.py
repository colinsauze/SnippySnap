from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    users = User.objects.all().select_related('profile')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    initials = models.CharField(max_length=10, blank=True)
    display_name = models.TextField()

    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

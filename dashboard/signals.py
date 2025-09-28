# managementapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from dashboard.models import ManageMember
from users.models import UserProfile  # adjust if needed

@receiver(post_save, sender=User)
def create_manage_member(sender, instance, created, **kwargs):
    if created:
        profile = None
        try:
            profile = UserProfile.objects.get(user=instance)
        except UserProfile.DoesNotExist:
            pass

        ManageMember.objects.create(
            member=instance,
            profile=profile,
            status=True  # default active
        )


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from dashboard.models import UserActivity
from chat.models import Message

# When user logs in
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserActivity.objects.create(user=user, action='login')

# When user logs out
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserActivity.objects.create(user=user, action='logout')

# When user sends a message
from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from dashboard.models import UserActivity

@receiver(post_save, sender=Message)
def log_message_activity(sender, instance, created, **kwargs):
    if created:
        # Get the last device used by the sender
        sender_activity = UserActivity.objects.filter(user=instance.sender).order_by('-created_at').first()
        sender_device = sender_activity.device if sender_activity else "Unknown"

        # Log sender activity
        UserActivity.objects.create(
            user=instance.sender,
            action="Sent Message",
            device=sender_device
        )

        # Get the last device used by the receiver
        receiver_activity = UserActivity.objects.filter(user=instance.receiver).order_by('-created_at').first()
        receiver_device = receiver_activity.device if receiver_activity else "Unknown"

        # Log receiver activity
        UserActivity.objects.create(
            user=instance.receiver,
            action="Received Message",
            device=receiver_device
        )

#logout and login signals
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from dashboard.models import AuditLog

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(user=user, action='login')

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(user=user, action='logout')


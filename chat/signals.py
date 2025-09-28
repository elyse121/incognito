from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Group

@receiver(post_migrate)
def create_default_group(sender, **kwargs):
    """Ensure the A_Members group exists after migrations."""
    if sender.name == "chat":  # only run for chat app
        group, created = Group.objects.get_or_create(
            name="A_Members",
            defaults={"creator": User.objects.first()}  # fallback creator
        )

        if created:
            print("✅ Default group 'A_Members' created.")

        # Add all users to the group
        group.members.set(User.objects.all())
        group.save()


@receiver(post_save, sender=User)
def add_new_user_to_default_group(sender, instance, created, **kwargs):
    """Whenever a new user is created, add them to A_Members group."""
    if created:
        try:
            group = Group.objects.get(name="A_Members")
            group.members.add(instance)
            group.save()
        except Group.DoesNotExist:
            # group will be created at next migrate, but just in case
            pass

from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from chat.models import Group

@receiver(post_migrate)
def create_default_group(sender, **kwargs):
    # Only run for the 'chat' app
    if sender.label != "chat":
        return

    # Ensure at least one user exists
    first_user = User.objects.first()
    if not first_user:
        return  # Skip until a user exists

    Group.objects.get_or_create(
        name="A_Members",
        defaults={"creator": first_user}
    )

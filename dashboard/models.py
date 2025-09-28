from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile

class ManageMember(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_memberships')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='manage_members')
    status = models.BooleanField(default=True)  # True = active, False = banned
    joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, default='member')

    def __str__(self):
        return f"{self.member.username} ({'Active' if self.status else 'Banned'})"


# chat/blocked_conversations/models.py
from django.db import models
from django.contrib.auth.models import User

class BlockedConversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user2")
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # prevent duplicate bans


#Notifications table.    

class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, null=True, blank=True)  # Make sure 'email' field exists if it's supposed to be there

    def __str__(self):
        return f'Notification from {self.sender.username}'
    

# User activity logging model
from django.db import models
from django.contrib.auth.models import User   # or your custom ManageMember

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)  # e.g., 'message', 'login', 'logout'
    device = models.CharField(max_length=255, blank=True, null=True)  # new column
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.device}) at {self.created_at}"

#reported posts
from django.db import models
from django.contrib.auth.models import User
from users.models import Post, Comment
from chat.models import Message

class Report(models.Model):
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_made"
    )
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_received"
    )
    messagereport = models.ForeignKey(
        Message, on_delete=models.CASCADE, null=True, blank=True, related_name="reports"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports"
    )
    post_id_ref = models.IntegerField(null=True, blank=True)  # <-- Explicit post_id column
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="reports"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically sync post_id_ref when a post is linked
        if self.post:
            self.post_id_ref = self.post.id
        super().save(*args, **kwargs)

    def __str__(self):
        if self.post:
            target = f"Post: {self.post.title}"
        elif self.comment:
            target = f"Comment by {self.comment.user}"
        elif self.reported_user:
            target = f"User: {self.reported_user.username}"
        elif self.messagereport:
            target = f"Message by {self.messagereport.sender.username}"
        else:
            target = "Unknown"
        return f"Report by {self.reporter} on {target}"


#warned users
class Warning(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='warnings_sent'
    )  # Admin or user sending the warning
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='warnings_received'
    )  # User receiving the warning
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name='warnings'
    )  # Optional: the post that triggered the warning
    message = models.TextField()  # Warning message
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Whether user has seen it

    def __str__(self):
        return f"Warning to {self.receiver.username} from {self.sender.username}"

#store_loggin_logout's
from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('critical', 'Critical Action'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.created_at}"
    
#privacy settings
from django.db import models

class PrivacySetting(models.Model):
    MESSAGE_ACCESS_CHOICES = [
        ("restricted", "Restricted"),
        ("full", "Full Access"),
    ]

    message_access = models.CharField(
        max_length=20, choices=MESSAGE_ACCESS_CHOICES, default="restricted"
    )

    user_data_export_allowed = models.BooleanField(default=True)

from chat.models import Group

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'group')

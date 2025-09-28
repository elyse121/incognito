from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    media = models.FileField(upload_to="chat_media/", blank=True, null=True)  # ✅ add this
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20] if self.content else '📎 Media'}"
    
"""class GroupChat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}" """


from django.db import models
from django.contrib.auth.models import User

#table for groups

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    members = models.ManyToManyField(User, related_name="member_groups")  # fixed clash
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupChat(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_sent_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # optional: private mention inside group
    receiver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_received_messages"
    )

    def __str__(self):
        return f"[{self.group.name}] {self.sender.username}: {self.message[:30]}"


from django.db import models
from django.contrib.auth.models import User
from users.models import TunnelSession  # Import tunnel sessions



from django.db import models
from django.contrib.auth.models import User
from users.models import TunnelSession

class TunnelMessage(models.Model):
    tunnel = models.ForeignKey(TunnelSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tunnel_sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tunnel_received_messages", null=True, blank=True)  # NEW FIELD
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
      # Allow null values for backward compatibility

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"[{self.tunnel.chat_room_id}] {self.sender.username} -> {self.receiver.username}: {self.content[:30]}"


from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"
class GroupChat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"


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

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('reported', 'Reported'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    photo = models.ImageField(upload_to='post_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    @property
    def is_video(self):
        if self.photo:
            return str(self.photo).lower().endswith(".mp4")
        return False

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user} likes {self.post.title}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.post.title}'
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
from django.utils import timezone

class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='memories/')
    caption = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Memories"
    
    def __str__(self):
        return f"{self.user.username}'s memory: {self.name}"
    
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    profile_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @staticmethod
    def generate_code():
        """Generate code like A5-QW-1E"""
        part1 = random.choice(string.ascii_uppercase) + random.choice(string.digits)
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        part3 = random.choice(string.ascii_uppercase) + random.choice(string.digits)
        return f"{part1}-{part2}-{part3}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class TunnelSession(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_tunnels')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_tunnels')
    tunnel_id = models.CharField(max_length=20, unique=True)
    chat_room_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    
    def generate_tunnel_id(self):
        return f"TN{random.randint(1000, 9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
    
    def generate_chat_room_id(self):
        return f"private_{self.initiator.id}_{self.recipient.id}_{int(timezone.now().timestamp())}"
    
    def save(self, *args, **kwargs):
        if not self.tunnel_id:
            self.tunnel_id = self.generate_tunnel_id()
        if not self.chat_room_id:
            self.chat_room_id = self.generate_chat_room_id()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        ordering = ['-created_at']


class TunnelOTP(models.Model):
    tunnel_session = models.ForeignKey(TunnelSession, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def generate_otp(self):
        return str(random.randint(100000, 999999))
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()



import uuid  # Add this import for verification token

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    profile_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # New field
    verification_token = models.CharField(max_length=36, unique=True, blank=True, null=True)  # For UUID

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @staticmethod
    def generate_code():
        """Generate code like A5-QW-1E"""
        part1 = random.choice(string.ascii_uppercase) + random.choice(string.digits)
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        part3 = random.choice(string.ascii_uppercase) + random.choice(string.digits)
        return f"{part1}-{part2}-{part3}"

    def generate_verification_token(self):
        """Generate a UUID for verification"""
        return str(uuid.uuid4())
    # models.py

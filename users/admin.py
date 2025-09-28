from django.contrib import admin
from users.models import Post, Comment, Like, UserProfile, TunnelSession, TunnelOTP  # Import UserProfile

# Define a custom admin class if you want to customize the display
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'photo')  # Include 'photo' in the list view
    search_fields = ('title', 'author__username')  # Allow searching by title or author username

# Register your models
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(UserProfile)  # Register the new model
from .models import Memory

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'caption')
    readonly_fields = ('created_at',)

# dashboard/admin.py

@admin.register(TunnelSession)
class TunnelSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tunnel_id', 'chat_room_id', 'initiator', 'recipient', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('tunnel_id', 'chat_room_id', 'initiator__username', 'recipient__username')
    readonly_fields = ('tunnel_id', 'chat_room_id', 'created_at')

@admin.register(TunnelOTP)
class TunnelOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'tunnel_session', 'otp_code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('otp_code', 'tunnel_session__tunnel_id', 'tunnel_session__chat_room_id')
    readonly_fields = ('otp_code', 'created_at', 'expires_at')

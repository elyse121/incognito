from django.contrib import admin
from .models import Post, Comment, Like, UserProfile  # Import UserProfile

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
from django.contrib import admin
from .models import Message, GroupChat, TunnelMessage, Group

admin.site.register(Message)
admin.site.register(GroupChat)
admin.site.register(TunnelMessage)  # ✅ Register tunnel messages
admin.site.register(Group)




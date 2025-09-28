from django.urls import path
from . import views

urlpatterns = [
    path('<str:room_name>/', views.chat_room, name='chat'),
    path('chat/room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('index/', views.redirect_to_user5_chat, name='go-to-user5-chat'),
    path('group/chat/', views.group_chat_view, name='group_chat'),

    path("fetch-messages/<str:chat_room_id>/", views.fetch_messages, name="fetch_messages"),

    # ✅ Tunnel chat URLs
    path('tunnel/<str:chat_room_id>/', views.tunnel_chat_view, name='tunnel_chat'),
    path('tunnel/<str:chat_room_id>/send/', views.send_tunnel_message, name='send_tunnel_message'),
    path('group_chat/<str:group_name>/', views.group_chat_view, name='group_chat'),
]

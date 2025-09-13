from django.urls import path
from . import views

urlpatterns = [
    # General pages
    path('', views.index_page, name="index"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_page, name="logout"),
    path('signup/', views.signup_view, name="signup"),
    path('chatter/', views.home_page, name="home"),

    # Post-related pages
    path('posts/', views.posts_page, name='posts'),
    path('posts/new/', views.new_post_view, name='new_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),

    # Memory
    path('add-memory/', views.add_memory, name='add-memory'),

    # User-specific chat
    path('elyse/', views.go_to_chat_with_user5, name='go-to-user5-chat'),

    # Tunnel pages
    path('souls/', views.souls_tunnel, name='souls-tunnel'),
    path('tunnel/', views.go_to_souls, name='go-to-souls'),

    # Private tunnel URLs
    path('tunnel/private/', views.private_tunnel, name='private-tunnel'),
    path('tunnel/initiate/', views.initiate_tunnel, name='initiate-tunnel'),
    path('tunnel/verify-otp/', views.verify_tunnel_otp, name='verify-tunnel-otp'),
    path('tunnel/chat/<str:chat_room_id>/', views.tunnel_chat, name='tunnel-chat'),
]

from django.urls import path
from . import views

urlpatterns = [
    # General pages
    path('', views.index_page, name="index"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_page, name="logout"),
    path('signup/', views.signup_view, name="signup"),
    path('chatter/', views.home_page, name="home"),
    path('verify/', views.verify_email, name="verify-email"),  # New route

    # Post-related pages
    path('posts/', views.posts_page, name='posts'),
    path('posts/new/', views.new_post_view, name='new_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),

    # Memory
    path('add-memory/', views.add_memory, name='add-memory'),

    # User-specific chat
    path('elyse/', views.go_to_chat_with_user5, name='go-to-user5-chat'),

    # Tunnel pages
    path('souls/', views.souls_tunnel, name='souls-tunnel'),
    path('tunnel/', views.go_to_souls, name='go-to-souls'),

    # Private tunnel URLs
    path('tunnel/private/', views.private_tunnel, name='private-tunnel'),
    path('tunnel/initiate/', views.initiate_tunnel, name='initiate-tunnel'),
    path('tunnel/verify-otp/', views.verify_tunnel_otp, name='verify-tunnel-otp'),
    path('tunnel/chat/<str:chat_room_id>/', views.tunnel_chat, name='tunnel-chat'),
]

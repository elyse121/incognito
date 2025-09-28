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

    # Chat tunnel
    path('tunnel/chat/<str:chat_room_id>/', views.tunnel_chat, name='tunnel-chat'),

    # Unlock archived messages
    path('tunnel/chat/<str:chat_room_id>/unlock/', views.unlock_archived_messages, name='unlock_archived_messages'),

    #banned users account's
    path('unbann_accounts/', views.unbann_accounts, name='unbann_accounts'),
    path('account_banned/', views.account_banned, name='account_banned'),
    path('ban/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban/<int:user_id>/', views.unban_user, name='unban_user'),
    path('banned_account_page/', views.banned_account_page, name='banned_account_page'),
    path("ban-user/<int:member_id>/", views.ban_user, name="ban_user"),
    path("unban-user/<int:member_id>/", views.unban_user, name="unban_user"),
    #path("banned/", views.banned_account_page, name="banned_account_page"),
    #path("contact-admin/", views.banned_page_contact_admin, name="contact_admin"),
    #path("contact-admin/", views.banned_account_page_contact_admin, name='contact_admin'), #banned_account_page_contact_admin
    path('banned/', views.banned_page, name='banned_page'),
    path('thank-you/', views.thank_you, name='thank_you'),
]

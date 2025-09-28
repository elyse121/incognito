from django.urls import path
from . import views

urlpatterns = [
    path('dashindex/', views.dashindex, name='dashindex'),
    path('allmembers/', views.allmembers_page, name='allmembers'),
    path('api/manage-members/', views.manage_members_api, name='manage_members_api'),
    path('dashboard/toggle-status/<int:member_id>/', views.toggle_member_status, name='toggle_member_status'),
    path('allmembers/', views.all_members_page, name='all_members_page'),
    #path('privatemessages/', views.privatemessages, name='privatemessages'),

    path("private-messages/", views.private_messages_admin, name="private_messages_admin"),
    path("api/check-admin-password/", views.check_admin_password, name="check_admin_password"),
    path("api/conversation/", views.conversation_api, name="conversation_api"),

    path('groupchats/', views.groupchats, name='groupchats'),
    path('darkmessages/', views.darkmessages, name='darkmessages'),
    path('reportemessages/', views.reportemessages, name='reportemessages'),
    path('privacydash/', views.privacydash, name='privacydash'),
    #path('admin_access_control/', views.admin_access_control, name='admin_access_control'),
    path('manageposts/', views.manageposts, name='manageposts'),
    path('useractivity/', views.useractivity, name='useractivity'),
    #path('prvtchat/', views.users_with_chat_data, name='prvtchat'),
    path('chatprivate/', views.private_messages_admin, name='chatprvate'),
    path("api/conversation/", views.conversation_view, name="conversation_view"),
    path("api/conversation/export/", views.export_conversation_csv, name="export_conversation_csv"),
    #path("api/toggle_ban_user/", views.toggle_ban_user, name="toggle_ban_user"),
    path("toggle-block-conversation/", views.toggle_block_conversation, name="toggle_block_conversation"),
    #path("contact-admin/", views.banned_account_page_contact_admin, name='contact_admin'), #banned_account_page_contact_admin
    path("private-messages/", views.private_messages_admin, name="private_messages_admin"),
    path("api/conversation/", views.conversation_api, name="conversation_api"),

    #noticitations count
    path('get_notification_count/', views.get_notification_count, name='get_notification_count'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('mark_all_read/', views.mark_all_read, name='mark_all_read'),
    path('mark_as_read/', views.mark_as_read_ajax, name='mark_as_read_ajax'),

    # User Activities
    path('dashboard_index_activities/', views.dashboard_index_activities, name='dashboard_index_activities'),
    path("user_activities/", views.user_activities, name="user_activities"),
    path("dashboard/api/user-details/<int:user_id>/", views.user_details, name="user_details"),

    #reported posts management
    path("reportedposts", views.reportedposts, name="reportedposts"),
    path("report/post/", views.report_post, name="report_post"),
    path("ban/<int:user_id>/", views.ban_user, name="ban_user"),
    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path('warn/<int:post_id>/', views.warn_user, name='warn_user'),
    path('posts/<int:post_id>/detail/', views.post_detail_api, name='post_detail_api'),
    path('posts/<int:post_id>/comments/', views.post_comments_api, name='post_comments_api'),
    
    # Approve or Reject Posts
    path("posts/<int:post_id>/approve/", views.approve_post, name="approve_post"),
    path("posts/<int:post_id>/reject/", views.reject_post, name="reject_post"),

    #Group Chats
    path('GroupMessages/', views.group_chat_view, name='GroupMessages'),
    path("GroupMessages/<int:group_id>/", views.group_chat_view, name="group_details"),
    path("GroupMessages/<int:group_id>/remove/<int:user_id>/", views.remove_member, name="remove_member"), #remove bttn
    #path("GroupMessages/<int:group_id>/toggle/<int:user_id>/", views.toggle_member_access, name="toggle_member_access"), #revoke access bttn 
    path("group/<int:group_id>/messages/", views.group_messages, name="group_messages"),
    path('chat/group/messages/<int:group_id>/', views.group_messages, name='group_messages'),
    path('chat/group/exit/<int:group_id>/', views.exit_group, name='exit_group'),
    path('group/<int:group_id>/members/', views.group_members, name='group_members'),

    #dark messages
    path('DarkMessages/', views.dark_messages_view, name='DarkMessages'),
    path('verify-admin-password/', views.verify_admin_password, name='verify_admin_password'),

    path('update_session_timeout/', views.update_session_timeout, name='update_session_timeout'),
    path('update_admin_credentials/', views.update_admin_credentials, name='update_admin_credentials'),
    path('update_message_access/', views.update_message_access, name='update_message_access'),
    path('toggle_export_permission/', views.toggle_export_permission, name='toggle_export_permission'),
    
]

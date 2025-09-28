# members/admin.py
from django.contrib import admin
#from dashboard.models import ManageMember, BlockedConversation, Notification, UserActivity, MessagesDevices
from dashboard.models import ManageMember, BlockedConversation, Notification, UserActivity, Report, Warning, AuditLog, PrivacySetting, GroupMembership



@admin.register(ManageMember)
class ManageMemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'member', 'profile_display', 'role', 'status', 'joined')
    search_fields = ('member__username', 'member__email')
    list_filter = ('status',)

    def profile_display(self, obj):
        return getattr(obj.profile, 'profile_picture', None) or "No Profile"
    profile_display.short_description = 'Profile'

    def member_id(self, obj):
        return obj.member.id
    member_id.short_description = 'Member ID'


@admin.register(BlockedConversation)
class BlockedConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'blocked_at')
    search_fields = ('user1__username', 'user2__username')
    list_filter = ('blocked_at',)   


#admin Notifications table
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'message', 'created_at', 'is_read')
    list_filter = ('read', 'created_at')
    search_fields = ('sender__username', 'message')
    readonly_fields = ('created_at',)

    def is_read(self, obj):
        return obj.read
    is_read.boolean = True  # shows a nice icon in admin
    is_read.admin_order_field = 'read'


#admin User activity logging

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action','device', 'created_at')   # columns shown in admin list
    list_filter = ('action', 'created_at', 'device', 'user')   # filters in sidebar
    search_fields = ('user__username', 'action')     # search bar
    ordering = ('-created_at',)  

#reported posts
@admin.register(Report)
class ReportedPostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'reporter', 
        'reported_user', 
        'post', 
        'post_id_display', 
        'comment', 
        'messagereport', 
        'reason', 
        'created_at'
    )
    search_fields = (
        'reporter__username', 
        'reported_user__username', 
        'post__title', 
        'comment__content', 
        'messagereport__content'
    )
    list_filter = ('created_at',)

    def post_id_display(self, obj):
        return obj.post_id   # Django auto field
    post_id_display.short_description = "Post ID"


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'post', 'created_at', 'read')
    list_filter = ('created_at', 'read')
    search_fields = ('sender__username', 'receiver__username', 'message', 'post__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

#login and logout admin
admin.register(AuditLog)
#privacy settings
admin.register(PrivacySetting)


admin.register(GroupMembership)

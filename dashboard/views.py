from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import ManageMember

#login
"""from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)  # Log user in

                # Check if admin
                if user.is_staff and user.is_superuser:
                    return redirect('dashindex')  # Admin dashboard
                else:
                    return redirect('index_page')  # Normal user page
            else:
                messages.error(request, "This account is inactive. Please contact admin.")
        else:
            messages.error(request, "Incorrect username or password.")

    return render(request, 'login.html')"""


@login_required
def dashindex(request):
    total_users = ManageMember.objects.count()

    return render(request, 'DASHBOARD/newcode/html/dashindex.html', {
        'total_users': total_users,
    })

@login_required
def allmembers_page(request):
    members = ManageMember.objects.select_related('member', 'profile').all()
    return render(request, 'DASHBOARD/newcode/html/allmembers.html', {'members': members})


from django.http import JsonResponse
from dashboard.models import ManageMember
@login_required
def manage_members_api(request):
    members = ManageMember.objects.select_related('member', 'profile').all()

    # Stats
    total_members = members.count()
    banned_members = members.filter(status=False).count()
    active_members = members.filter(status=True).count()

    data = []
    for m in members:
        data.append({
            'id': m.id,
            'username': m.member.username,
            'email': m.member.email,
            'role': m.role,
            'joined': m.joined.isoformat(),
            'status': 'active' if m.status else 'banned',
            'avatar': m.profile.profile_picture.url if m.profile and m.profile.profile_picture else '/static/default-avatar.png',
        })

    return render(request, 'DASHBOARD/newcode/html/allmembers.html', {
        'members': data,
        'total_members': total_members,
        'banned_members': banned_members,
        'active_members': active_members
    })

@login_required
def all_members_page(request):
    return render(request, 'DASHBOARD/newcode/html/allmembers.html')


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt  # for testing; replace with proper CSRF handling
@require_POST
def toggle_member_status(request, member_id):
    try:
        member = ManageMember.objects.get(id=member_id)
        member.status = not member.status
        member.save()
        return JsonResponse({'success': True})
    except ManageMember.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)

#prvt cht
from django.db.models import Q, Max
from django.shortcuts import render
from dashboard.models import ManageMember
from chat.models import Message

@login_required
def users_with_chat_data(request):
    user_ids_with_msgs = Message.objects.values_list('sender_id', flat=True).union(
        Message.objects.values_list('receiver_id', flat=True)
    )
    members = ManageMember.objects.select_related('member', 'profile').filter(member_id__in=user_ids_with_msgs)

    table_data = []

    for mm in members:
        user_obj = mm.member

        partners = Message.objects.filter(
            Q(sender=user_obj) | Q(receiver=user_obj)
        ).values_list('sender_id', 'receiver_id')

        partner_ids = set()
        for sender_id, receiver_id in partners:
            if sender_id != user_obj.id:
                partner_ids.add(sender_id)
            if receiver_id != user_obj.id:
                partner_ids.add(receiver_id)

        chat_partners_count = len(partner_ids)

        last_active = Message.objects.filter(
            Q(sender=user_obj) | Q(receiver=user_obj)
        ).aggregate(last_time=Max('timestamp'))['last_time']

        # Get avatar URL or fallback
        avatar_url = ''
        if mm.profile and mm.profile.profile_picture:
            avatar_url = mm.profile.profile_picture.url
        else:
            avatar_url = '/static/default-avatar.png'  # or any default image you have

        table_data.append({
            'username': user_obj.username,
            'avatar': avatar_url,
            'chat_partners': chat_partners_count,
            'last_active': last_active,
            'status': "Active" if mm.status else "Banned",
        })

    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html', {
        'users': table_data
    })




"""from django.db.models import Q
from django.shortcuts import render
from dashboard.models import ManageMember
from chat.models import Message
from django.contrib.auth.models import User

def private_messages_admin(request):
    # Get all user IDs who sent or received messages
    user_ids_with_msgs = set(
        Message.objects.values_list('sender_id', flat=True)
        .union(Message.objects.values_list('receiver_id', flat=True))
    )

    members_data = []

    # Loop over all users who appear in messages
    users = User.objects.filter(id__in=user_ids_with_msgs)

    for user in users:
        # Get all messages where user is sender or receiver
        user_msgs = Message.objects.filter(Q(sender=user) | Q(receiver=user))

        # Get unique partner IDs (people who sent or received messages with this user, excluding self)
        senders = set(
            user_msgs.exclude(sender=user).values_list('sender_id', flat=True)
        )
        receivers = set(
            user_msgs.exclude(receiver=user).values_list('receiver_id', flat=True)
        )
        partner_ids = senders.union(receivers)

        partners = User.objects.filter(id__in=partner_ids)

        # Last active timestamp from messages
        last_active_msg = user_msgs.order_by('-timestamp').first()
        last_active = last_active_msg.timestamp if last_active_msg else None

        # ✅ Fetch status from ManageMember
        member_record = ManageMember.objects.filter(member=user).first()
        status = member_record.status if member_record else None

        members_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.userprofile.profile_picture.url if hasattr(user, 'userprofile') and user.userprofile.profile_picture else 'https://via.placeholder.com/40',
            'partners_count': partners.count(),
            'last_active': last_active,
            'status': status,  # ✅ Corrected status here
            'partners': [
                {
                    'id': p.id,
                    'username': p.username,
                    'email': p.email,
                    'avatar_url': p.userprofile.profile_picture.url if hasattr(p, 'userprofile') and p.userprofile.profile_picture else 'https://via.placeholder.com/50',
                } for p in partners
            ]
        })

    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html', {
        'members_data': members_data
    })"""


    # dashboard/views.py
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

from dashboard.models import ManageMember
from chat.models import Message


# Existing view for admin page
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import Message
from dashboard.models import ManageMember

@login_required
def is_admin(user):
    return user.is_active and user.is_staff and user.is_superuser


@login_required
@user_passes_test(is_admin)
def private_messages_admin(request):
    # Search query
    search_query = request.GET.get("q", "").strip()
    # Status filter
    status_filter = request.GET.get("status", "").lower()

    # Get all user IDs who sent or received messages
    user_ids_with_msgs = set(
        Message.objects.values_list("sender_id", flat=True).union(
            Message.objects.values_list("receiver_id", flat=True)
        )
    )

    users = User.objects.filter(id__in=user_ids_with_msgs)

    # Apply search
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    # Apply status filter (based on ManageMember table)

    if status_filter == "active":
        users = users.filter(managed_memberships__status=True)
    elif status_filter == "banned":
        users = users.filter(managed_memberships__status=False)


    members_data = []
    for user in users:
        user_msgs = Message.objects.filter(Q(sender=user) | Q(receiver=user))

        senders = set(user_msgs.exclude(sender=user).values_list("sender_id", flat=True))
        receivers = set(user_msgs.exclude(receiver=user).values_list("receiver_id", flat=True))
        partner_ids = senders.union(receivers)

        partners = User.objects.filter(id__in=partner_ids)

        last_active_msg = user_msgs.order_by("-timestamp").first()
        last_active = last_active_msg.timestamp if last_active_msg else None

        member_record = ManageMember.objects.filter(member=user).first()
        status = member_record.status if member_record else None

        members_data.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.userprofile.profile_picture.url
                if hasattr(user, "userprofile") and user.userprofile.profile_picture
                else "https://via.placeholder.com/40",
                "partners_count": partners.count(),
                "last_active": last_active,
                "status": status,
                "partners": [
                    {
                        "id": p.id,
                        "username": p.username,
                        "email": p.email,
                        "avatar_url": p.userprofile.profile_picture.url
                        if hasattr(p, "userprofile") and p.userprofile.profile_picture
                        else "https://via.placeholder.com/50",
                    }
                    for p in partners
                ],
            }
        )

    return render(
        request,
        "DASHBOARD/newcode/html/PrivateMessages.html",
        {
            "members_data": members_data,
            "search_query": search_query,
            "status_filter": status_filter,  # pass back to template
        },
    )



@login_required
@user_passes_test(is_admin)
def check_admin_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user and user.is_active and user.is_staff and user.is_superuser:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Invalid admin credentials"}, status=403)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
@user_passes_test(is_admin)
def conversation_api(request):
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        user_id = int(user_id)
        partner_id = int(partner_id)
    except ValueError:
        return JsonResponse({"error": "Invalid parameters"}, status=400)

    messages = (
        Message.objects.filter(
            Q(sender_id=user_id, receiver_id=partner_id)
            | Q(sender_id=partner_id, receiver_id=user_id)
        )
        .order_by("timestamp")
        .select_related("sender", "receiver")
    )

    data = [
        {
            "id": msg.id,
            "sender_id": msg.sender.id,
            "sender_username": msg.sender.username,
            "receiver_id": msg.receiver.id,
            "receiver_username": msg.receiver.username,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in messages
    ]

    return JsonResponse({"messages": data})

@login_required
# ✅ New API for conversation
def conversation_api(request):
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return JsonResponse({"error": "Missing user_id or partner_id"}, status=400)

    try:
        messages = Message.objects.filter(
            (Q(sender_id=user_id, receiver_id=partner_id)) |
            (Q(sender_id=partner_id, receiver_id=user_id))
        ).order_by("timestamp")

        data = [
            {
                "id": msg.id,
                "sender_id": msg.sender.id,
                "sender_username": msg.sender.username,
                "message": msg.content,  # <-- adjust if your field is different
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]

        return JsonResponse({"messages": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from chat.models import Message
from django.contrib.auth.models import User

@login_required
def get_conversation(request):
    user_id = request.user.id
    partner_id = request.GET.get('partner_id')

    if not partner_id:
        return JsonResponse({'error': 'partner_id is required'}, status=400)

    try:
        partner = User.objects.get(id=partner_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Partner not found'}, status=404)

    # Fetch messages between the two users, ordered by timestamp ascending
    messages = Message.objects.filter(
        (Q(sender_id=user_id) & Q(receiver_id=partner_id)) |
        (Q(sender_id=partner_id) & Q(receiver_id=user_id))
    ).order_by('timestamp')

    # Serialize messages into a list of dicts
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_username': msg.sender.username,
            'receiver_id': msg.receiver_id,
            'receiver_username': msg.receiver.username,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
        })

    return JsonResponse({
        'partner': {
            'id': partner.id,
            'username': partner.username,
            # add avatar url if needed here
        },
        'messages': messages_list,
    })

"""    

import csv
from io import StringIO
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from chat.models import Message

@login_required
@staff_member_required  # only admin/staff can use this
@require_GET
def conversation_view(request):
    """
    JSON API for messages between user_id and partner_id
    """
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return JsonResponse({"error": "user_id and partner_id are required"}, status=400)

    try:
        user_id = int(user_id)
        partner_id = int(partner_id)
    except ValueError:
        return JsonResponse({"error": "IDs must be integers"}, status=400)

    # Ensure users exist
    get_object_or_404(User, id=user_id)
    get_object_or_404(User, id=partner_id)

    qs = (
        Message.objects
        .filter(
            Q(sender_id=user_id, receiver_id=partner_id) |
            Q(sender_id=partner_id, receiver_id=user_id)
        )
        .select_related("sender", "receiver")
        .order_by("timestamp")
    )

    messages_data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_username": m.sender.username,
            "receiver_id": m.receiver_id,
            "message": m.content,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in qs
    ]

    return JsonResponse({"messages": messages_data}, status=200)

@login_required
@staff_member_required
@require_GET
def export_conversation_csv(request):
    """
    Exports conversation as CSV for given user_id + partner_id
    """
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return HttpResponse("Missing parameters", status=400)

    qs = (
        Message.objects
        .filter(
            Q(sender_id=user_id, receiver_id=partner_id) |
            Q(sender_id=partner_id, receiver_id=user_id)
        )
        .select_related("sender", "receiver")
        .order_by("timestamp")
    )

    # Prepare CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Sender", "Receiver", "Message"])

    for m in qs:
        writer.writerow([
            m.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            m.sender.username,
            m.receiver.username,
            m.content.replace("\n", " ")  # keep CSV one-line
        ])

    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="conversation_{user_id}_{partner_id}.csv"'
    return response


#forban

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.models import User

from dashboard.models import BlockedConversation
from chat.models import Message

@login_required
def is_blocked(user1, user2):
    """
    Returns True if user1 and user2 are blocked from chatting with each other.
    Checks both directions.
    """
    return BlockedConversation.objects.filter(
        (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
    ).exists()


@login_required
@require_POST
def toggle_block_conversation(request):
    """
    Toggle block/unblock between two users.
    """
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    user1_id = request.POST.get("user1_id")
    user2_id = request.POST.get("user2_id")

    if not user1_id or not user2_id:
        return JsonResponse({"error": "Missing user ids"}, status=400)

    try:
        user1 = User.objects.get(id=int(user1_id))
        user2 = User.objects.get(id=int(user2_id))

        # Check if already blocked
        blocked = BlockedConversation.objects.filter(
            (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
        ).first()

        if blocked:
            # Unblock
            blocked.delete()
            action = "unblocked"
            blocked_status = False
        else:
            # Block conversation
            BlockedConversation.objects.create(user1=user1, user2=user2)
            action = "blocked"
            blocked_status = True

            # Send emails to both users
            subject = "Chat Restriction Notice"
            from_email = "elyseniyonzima202@gmail.com"
            send_mail(subject, f"You are not allowed to chat with {user2.username} anymore.", from_email, [user1.email], fail_silently=False)
            send_mail(subject, f"You are not allowed to chat with {user1.username} anymore.", from_email, [user2.email], fail_silently=False)

        return JsonResponse({
            "success": True,
            "blocked": blocked_status,
            "message": f"Conversation between {user1.username} and {user2.username} is now {action}."
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def send_message(request):
    """
    Save a message if the conversation is not blocked.
    """
    receiver_id = request.POST.get("receiver_id")
    content = request.POST.get("content")

    if not receiver_id or not content:
        return JsonResponse({"error": "Missing receiver or content"}, status=400)

    try:
        receiver = User.objects.get(id=int(receiver_id))

        # Check if conversation is blocked
        if is_blocked(request.user, receiver):
            return JsonResponse({"error": "You are not allowed to chat with this user."}, status=403)

        # Save message
        msg = Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return JsonResponse({"success": True, "message": msg.content})

    except User.DoesNotExist:
        return JsonResponse({"error": "Receiver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#save Notification messages from contact admin form(BannedAccounts)
"""from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.forms import NotificationForm
from dashboard.models import Notification

@login_required  # Ensure the user is logged in
def banned_account_page_contact_admin(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            # Save the form data and assign the sender
            notification = form.save(commit=False)  # Don't save yet
            notification.sender = request.user  # Set the sender as the logged-in user
            notification.save()  # Save to the database
            
            messages.success(request, "Your message has been sent to the admin.")
            return redirect('posts')  # Redirect after successful submission
        else:
            messages.error(request, "There was an error submitting your message.")
    else:
        form = NotificationForm()

    return render(request, 'BannedAccount.html', {'form': form})
"""


# coount notifications budger
# views.py
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from dashboard.models import Notification

@login_required
def get_notification_count(request):
    count = Notification.objects.filter(read=False).count()
    
    return JsonResponse({'count': count})


# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from dashboard.models import Notification
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages

@login_required
def view_notifications(request):
    # Get filter parameter
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    notifications = Notification.objects.all().order_by('-created_at')
    
    # Apply filters
    if filter_type == 'unread':
        notifications = notifications.filter(read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Mark single notification as read
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        notification_id = request.POST.get('mark_as_read')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.read = True
            notification.save()
            messages.success(request, 'Notification marked as read.')
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found.')
        return redirect('view_notifications')
    
    context = {
        'page_obj': page_obj,
        'unread_count': Notification.objects.filter(read=False).count(),
    }
    return render(request, 'DASHBOARD/newcode/html/Notifications.html', context)

@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(read=False).update(read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('view_notifications')

@login_required
def mark_as_read_ajax(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



#user activity logging view
from django.shortcuts import render
from django.db.models import Count
from django.utils.timezone import now, timedelta
from dashboard.models import UserActivity
from django.contrib.auth.models import User
import datetime

@login_required
def user_activity_chart(request):
    # Example: show data for the last 30 days
    end_date = now().date()
    start_date = end_date - timedelta(days=29)

    # Prepare labels (dates)
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

    # Count activities per day
    activities = (
        UserActivity.objects
        .filter(created_at__date__range=[start_date, end_date])
        .extra({'day': "date(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Map counts to dates
    data_dict = {a['day'].strftime('%Y-%m-%d'): a['count'] for a in activities}
    data = [data_dict.get(date, 0) for date in labels]

    context = {
        'labels': labels,
        'data': data,
    }

    return render(request, 'DASHBOARD/newcode/html/dashindex.html', context)



from django.shortcuts import render
from dashboard.models import UserActivity

def dashboard_index_activities(request):
    activities = UserActivity.objects.select_related("user").order_by("-created_at")[:20]  
    
    return render(request, "DASHBOARD/newcode/html/dashindex.html", {"activities": activities})


# User Activities View
import json
from itertools import groupby
from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from users.models import UserProfile
from django.contrib.auth.models import User
from dashboard.models import UserActivity
from chat.models import Message
from dashboard.models import ManageMember

@login_required
def user_activities(request):
    # -------------------------------
    # 0. Filter & Search
    # -------------------------------
    filter_type = request.GET.get("filter", "All")
    search_query = request.GET.get("q", "").strip()

    # -------------------------------
    # 1. Latest 10 activities
    # -------------------------------
    activities_qs = UserActivity.objects.select_related("user").order_by("-created_at")

    if filter_type == "Messages":
        activities_qs = activities_qs.filter(action__icontains="message")
    elif filter_type == "Logins":
        activities_qs = activities_qs.filter(action__icontains="logged in")
    elif filter_type == "Reports":
        activities_qs = activities_qs.filter(action__icontains="report")

    if search_query:
        activities_qs = activities_qs.filter(
            Q(user__username__icontains=search_query) |
            Q(action__icontains=search_query)
        )

    # pagination (5 per page)
    paginator = Paginator(activities_qs, 3)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_ids = [a.user_id for a in page_obj]
    profiles = UserProfile.objects.filter(user_id__in=user_ids)
    profile_map = {p.user_id: p for p in profiles}

    activities = []
    for act in page_obj:
        profile = profile_map.get(act.user_id)
        activities.append({
            "username": act.user.username,
            "action": act.action,
            "device": act.device or "Unknown device",
            "avatar": profile.profile_picture.url if profile and profile.profile_picture else "/static/images/default-avatar.png",
            "timestamp": act.created_at,
        })


    """user_ids = [a.user_id for a in activities_qs]
    profiles = UserProfile.objects.filter(user_id__in=user_ids)
    profile_map = {p.user_id: p for p in profiles}"""

    """activities = []
    for act in activities_qs[:10]:
        profile = profile_map.get(act.user_id)
        activities.append({
            "username": act.user.username,
            "action": act.action,
            "device": act.device or "Unknown device",
            "avatar": profile.profile_picture.url if profile and profile.profile_picture else "/static/images/default-avatar.png",
            "created_at": act.created_at,
        })"""

    # -------------------------------
    # 2. Stats Cards
    # -------------------------------
    today = timezone.now()
    yesterday = today - timedelta(days=1)

    # Active users (status != "banned")
    active_users_count = ManageMember.objects.filter(status=False).count() #error to count ctive users (status != "banned")!!!

    # Messages in last 24 hours
    messages_count = Message.objects.filter(timestamp__gte=yesterday).count()
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    prev_24h = now - timedelta(hours=48)

    # Messages within last 24 hours
    messages_last_24h = Message.objects.filter(timestamp__gte=last_24h).count()

    # Messages in previous 24–48 hours
    messages_prev_24h = Message.objects.filter(timestamp__gte=prev_24h, timestamp__lt=last_24h).count()

    # Calculate percentage growth (avoid division by zero)
    if messages_prev_24h > 0:
        percentage_change = ((messages_last_24h - messages_prev_24h) / messages_prev_24h) * 100
    else:
        percentage_change = 100 if messages_last_24h > 0 else 0

    stats = {
        "messages": messages_last_24h,
        "percentage": round(percentage_change, 2),
    }
    
    # Reports in last 24 hours
    reports_count = UserActivity.objects.filter(
        action__icontains="report",
        created_at__gte=yesterday
    ).count()

    reports_last_24h = UserActivity.objects.filter(
        action__icontains="report",
        created_at__gte=last_24h
    ).count()

    # Reports in previous 24–48h
    reports_prev_24h = UserActivity.objects.filter(
        action__icontains="report",
        created_at__gte=prev_24h,
        created_at__lt=last_24h
    ).count()

    # Calculate growth %
    if reports_prev_24h > 0:
        reports_percentage = ((reports_last_24h - reports_prev_24h) / reports_prev_24h) * 100
    else:
        reports_percentage = 100 if reports_last_24h > 0 else 0

    stats = {
        "reports": reports_last_24h,
        "reports_percentage": round(reports_percentage, 2),
        "reports_percentage_abs": round(abs(reports_percentage), 2),
    }

    # Average session (from login/logout)
    sessions = []
    login_logout_qs = UserActivity.objects.filter(
        action__in=['logged in', 'logged out'],
        created_at__date=today.date()
    ).order_by('user_id', 'created_at')

    for user_id, acts in groupby(login_logout_qs, key=lambda x: x.user_id):
        acts = list(acts)
        login_time = None
        for act in acts:
            if 'logged in' in act.action.lower():
                login_time = act.created_at
            elif 'logged out' in act.action.lower() and login_time:
                duration = act.created_at - login_time
                sessions.append(duration.total_seconds())
                login_time = None

    avg_session_minutes = round(sum(sessions)/len(sessions)/60, 1) if sessions else 0


    

    # -------------------------------
    # 3. Top active users today
    # -------------------------------
    user_actions_today = (
        UserActivity.objects
        .filter(created_at__date=today.date())
        .values("user")
        .annotate(action_count=Count("id"))
        .order_by("-action_count")[:5]
    )

    profiles_today = UserProfile.objects.filter(user_id__in=[ua["user"] for ua in user_actions_today])
    profile_map_today = {p.user_id: p for p in profiles_today}

    top_users = []
    for ua in user_actions_today:
        profile = profile_map_today.get(ua["user"])
        user_obj = profile.user if profile else None
        top_users.append({
            "username": user_obj.username if user_obj else "Unknown User",
            "avatar": profile.profile_picture.url if profile and profile.profile_picture else "/static/images/default-avatar.png",
            "action_count": ua["action_count"],
        })

    # -------------------------------
    # 4. Activity timeline chart
    # -------------------------------
    activities_by_day = (
        UserActivity.objects
        .filter(created_at__date__lte=today.date())
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    labels = [str(a["day"]) for a in activities_by_day]
    data = [a["count"] for a in activities_by_day]

    # -------------------------------
    # 5. Render
    # -------------------------------
    return render(request, "DASHBOARD/newcode/html/UserActivity.html", {
        "activities": activities,
        "page_obj": page_obj,
        "top_users": top_users,
        "timeline_labels": json.dumps(labels),
        "timeline_data": json.dumps(data),
        "active_filter": filter_type,
        "search_query": search_query,
        # Stats Cards
        "stats": {
            "active_users": active_users_count,
            "messages": messages_count,
            "reports": reports_count,
            "avg_session": avg_session_minutes,
        }
    })

#about view details
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import UserProfile, ManageMember, UserActivity
from django.contrib.auth.models import User

@login_required
def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.filter(user=user).first()
    status = ManageMember.objects.filter(user=user).first()
    activity = UserActivity.objects.filter(user=user).last()

    data = {
        "profile": profile.full_name if profile else user.username,  # use profile as title
        "username": user.username,
        "email": user.email,
        "status": status.status if status else "Unknown",
        "action": activity.action if activity else "No activity"
    }
    return JsonResponse(data)


#send message
from dashboard.models import UserActivity
from chat.models import Message
#from dashboard.models import MessageDevice
from user_agents import parse  

@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("content")
        receiver_id = request.POST.get("receiver_id")

        message = Message.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content
        )

        # Detect device
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        parsed_agent = parse(user_agent)
        device_info = f"{parsed_agent.os.family} - {parsed_agent.browser.family}"

        # Log activity
        UserActivity.objects.create(
            user=request.user,
            action="Sent Message",
            device=device_info
        )

        return redirect("inbox")  # or wherever


#ManagePosts view

"""from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from users.models import Post, UserProfile
from dashboard.models import Report, Warning
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def reportedposts(request):
    since = timezone.now() - timedelta(days=1)

    # Stats
    total_posts = Post.objects.filter(created_at__gte=since).count()
    reported_count = Report.objects.filter(created_at__gte=since).count()
    total_warnings = Warning.objects.filter(created_at__gte=since).count()

    # Search + filter
# --- NEW ---
    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "all")

    # Base queryset
    posts = Post.objects.select_related("author", "author__userprofile").all()

    # Apply search (username or content)
    if search_query:
        posts = posts.filter(
            Q(author__username__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Apply status filter
    if status_filter == "reported":
        posts = posts.filter(reports__isnull=False).distinct()
    elif status_filter == "active":
        posts = posts.filter(reports__isnull=True)
    elif status_filter == "pending":
        posts = posts.filter(status="pending")  # only if you add a field
    elif status_filter == "archived":
        posts = posts.filter(status="archived")  # only if you add a field

    posts = posts.order_by("-created_at")

    # Check filter (all vs reported)
    filter_type = request.GET.get("filter", "all")

    if filter_type == "reported":
        posts = Post.objects.filter(reports__isnull=False).select_related(
            "author", "author__userprofile"
        ).distinct().order_by("-created_at")
        active_tab = "reported"
    else:
        posts = Post.objects.select_related(
            "author", "author__userprofile"
        ).all().order_by("-created_at")
        active_tab = "all"

    # ✅ Pagination (5 items per page)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Build posts_data for current page only
    posts_data = []
    for post in page_obj:
        is_reported = Report.objects.filter(post=post).exists()
        profile = getattr(post.author, "userprofile", None)

        posts_data.append({
            "id": post.id,
            "author_id": post.author.id,
            "author_username": post.author.username,
            "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else "",
            "content": post.content,
            "media": post.photo.url if post.photo else None,
            "date": post.created_at,
            "status": "Reported" if is_reported else "Active",
        })

    context = {
        "total_posts": total_posts,
        "reported": reported_count,
        "total_warnings": total_warnings,
        "posts_data": posts_data,
        "search_query": search_query,
        "status_filter": status_filter,
        "active_tab": active_tab,
        "page_obj": page_obj,   # ✅ pass page object to template
    }
    return render(request, "DASHBOARD/newcode/html/ManagePost.html", context)"""


from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from users.models import Post, UserProfile
from dashboard.models import Report, Warning
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def reportedposts(request):
    since = timezone.now() - timedelta(days=1)

    # Stats cards
    total_posts = Post.objects.filter(created_at__gte=since).count()
    reported_count = Report.objects.filter(created_at__gte=since).count()
    total_warnings = Warning.objects.filter(created_at__gte=since).count()
    
    # 👇 Count distinct users who authored posts
    total_users = Post.objects.values("author").distinct().count()

    # --- Filters + search---
    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "all")
    filter_type = request.GET.get("filter", "all")

    # Base queryset
    posts = Post.objects.select_related("author", "author__userprofile").all()

    # Apply search (username or content)
    if search_query:
        posts = posts.filter(
            Q(author__username__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Apply status filter
    if status_filter == "reported":
        posts = posts.filter(reports__isnull=False).distinct()
    elif status_filter == "active":
        posts = posts.filter(reports__isnull=True).distinct()
    elif status_filter == "pending":
        posts = posts.filter(status="pending")  # only if your Post has 'status'
    elif status_filter == "archived":
        posts = posts.filter(status="archived")  # only if your Post has 'status'

    # Apply filter type (tab selection)
    if filter_type == "reported":
        posts = posts.filter(reports__isnull=False).distinct()
        active_tab = "reported"
    else:
        active_tab = "all"

    posts = posts.order_by("-created_at")

    # ✅ Pagination (5 per page)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ✅ Build posts_data only for current page
    posts_data = []
    for post in page_obj:
        is_reported = Report.objects.filter(post=post).exists()
        profile = getattr(post.author, "userprofile", None)

        posts_data.append({
            "id": post.id,
            "author_id": post.author.id,
            "author_username": post.author.username,
            "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else "",
            "content": post.content,
            "media": post.photo.url if post.photo else None,
            "date": post.created_at,
            "status": "Reported" if is_reported else "Active",
        })

    context = {
        "total_posts": total_posts,
        "reported": reported_count,
        "total_warnings": total_warnings,
        "total_users": total_users,
        "posts_data": posts_data,
        "search_query": search_query,
        "status_filter": status_filter,
        "active_tab": active_tab,
        "page_obj": page_obj,
    }
    return render(request, "DASHBOARD/newcode/html/ManagePost.html", context)



#about eyepopupbox managepost(comment+posts)
from django.http import JsonResponse
from users.models import Post, Comment, UserProfile

@login_required
def post_detail_api(request, post_id):
    post = Post.objects.select_related("author").get(id=post_id)
    profile = getattr(post.author, "userprofile", None)

    return JsonResponse({
        "id": post.id,
        "author_username": post.author.username,
        "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else "",
        "content": post.content,
        "media": post.photo.url if post.photo else "",
        "date": post.created_at.strftime("%B %d, %Y at %I:%M %p"),
        "likes": post.likes.count(),
        "comments_count": post.comments.count(),
    })

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from users.models import Post
import logging
logger = logging.getLogger(__name__)

@require_POST
def approve_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        post.status = "active"
        post.save(update_fields=["status"])
        logger.info(f"Approved post {post_id}")
        return JsonResponse({"success": True, "message": "✅ Post approved and set to Active."})
    except Exception as e:
        logger.error(f"Error approving post {post_id}: {str(e)}")
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=400)

@login_required
@require_POST
def reject_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        post.status = "archived"
        post.save(update_fields=["status"])
        return JsonResponse({"success": True, "message": "❌ Post rejected and set to Archived."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=400)


@login_required
def post_comments_api(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.select_related("user").order_by("-created_at")  # use related_name 'comments'

    data = []
    for c in comments:
        profile = getattr(c.user, "userprofile", None)
        data.append({
            "author_username": c.user.username,
            "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else "",
            "content": c.content,
            "date": c.created_at.strftime("%B %d, %Y at %I:%M %p"),
        })

    return JsonResponse({"comments": data})

# Ban User
@login_required
def ban_user(request, user_id):
    if request.method == "POST":
        # Get the user's ManageMember record
        member_record = get_object_or_404(ManageMember, member_id=user_id)
        # Toggle status: True -> False (ban), False -> True (unban)
        member_record.status = not member_record.status
        member_record.save()
    return redirect('reportedposts')

@login_required
def delete_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return redirect("reportedposts")

#waring message send to user who been reported
from dashboard.models import Warning

@login_required
def warn_user(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        # Example message (you can also customize it using a form)
        warning_message = f"Your post titled '{post.title}' was reported. Please review your content."
        
        Warning.objects.create(
            sender=request.user,         # the admin sending the warning
            receiver=post.author,        # the user who posted
            post=post,
            message=warning_message
        )
        messages.success(request, f"Warning sent to {post.author.username} successfully.")
    return redirect('reportedposts')

#report save into report table
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Post, Comment
from dashboard.models import Report

@login_required
def report_post(request):
    if request.method == "POST":
        reporter = request.user
        post_id = request.POST.get("post_id")
        comment_id = request.POST.get("comment_id")
        reason = request.POST.get("reason")
        details = request.POST.get("details", "")

        post = get_object_or_404(Post, id=post_id)
        comment = None
        if comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                comment = None

        Report.objects.create(
            reporter=reporter,
            reported_user=post.author,  # who wrote the post
            post=post,
            post_id_ref=post.id,        # 👈 explicitly store the post ID too
            comment=comment,
            reason=f"{reason} - {details}" if details else reason,
        )

        return redirect("posts")  # redirect to dashboard or success page

    return redirect("posts_page")


#GroupChat_Views
"""from django.shortcuts import render
from chat.models import GroupChat
from django.contrib.auth.models import User
from chat.models import Message, GroupChat

def group_chat_view(request):
    groups = GroupChat.objects.prefetch_related('members', 'creator')

    groups_data = []

    for group in groups:
        groups_data.append({
            "id": group.id,
            "name": group.group_name,
            "avatarText": "".join([w[0] for w in group.group_name.split()][:2]).upper(),
            "membersCount": group.members.count() + 1,  # include creator
            "lastActivity": group.timestamp.strftime("%b %d, %Y, %H:%M"),
            "status": "active" if group.status == "admin" else group.status,
            "created": group.timestamp.strftime("%b %d, %Y"),
            "admin": group.creator.username,
            "totalMessages": group.members.count() + 1,  # or track real messages later
            "members": [
                {
                    "id": group.creator.id,
                    "name": group.creator.username,
                    "status": "admin",
                    "lastSeen": "Online",  # You can fetch actual last login
                    "avatar": getattr(group.creator.userprofile, "profile_picture", "https://via.placeholder.com/50")
                    if hasattr(group.creator, "userprofile") else "https://via.placeholder.com/50"
                }
            ] + [
                {
                    "id": member.id,
                    "name": member.username,
                    "status": "active",
                    "lastSeen": "Online",  # or fetch last login
                    "avatar": getattr(member.userprofile, "profile_picture", "https://via.placeholder.com/50")
                    if hasattr(member, "userprofile") else "https://via.placeholder.com/50"
                }
                for member in group.members.all()
            ]
        })

    return render(request, "DASHBOARD/newcode/html/GroupMessages.html", {"groups_data": groups_data})
"""

#### Groups On dashboard ####
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from chat.models import Group, GroupChat

@login_required
def group_chat_view(request, group_id=None):
    search_query = request.GET.get("search", "")

    # Get all groups (or filter by user if needed)
    #groups = Group.objects.all()  # replace with your actual queryset

    if search_query:
        groups = groups.filter(Q(name__icontains=search_query))
    # Groups list with member count and last activity
    groups = (
        Group.objects.annotate(
            membersCount=Count("members", distinct=True),
            lastActivity=Max("messages__timestamp"),
        )
        .all()
        .order_by("-lastActivity")
    )

    selected_group = None
    members = None

    if group_id:
        selected_group = get_object_or_404(Group, id=group_id)
        members = selected_group.members.all()

    return render(
        request,
        "DASHBOARD/newcode/html/GroupMessages.html",
        {
            "groups": groups,
            "selected_group": selected_group,
            "members": members,
            "search_query": search_query,
        },
    )

def group_messages(request, group_id):
    messages = GroupChat.objects.filter(group_id=group_id).order_by("-timestamp")
    return JsonResponse({
        "messages": [
            {
                "id": m.id,
                "sender": m.sender.username,
                "text": m.message,
                "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M")
            }
            for m in messages
        ]
    })

@login_required
@require_POST
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    user = get_object_or_404(User, id=user_id)

    # Remove member
    group.members.remove(user)

    # Send email notification
    subject = f"You have been removed from the group {group.name}"
    message = (
        f"Hello {user.username},\n\n"
        f"You are no longer a member of the group \"{group.name}\".\n"
        "You will not be able to view messages, send or receive anything, "
        "or see its members.\n\n"
        "Regards,\nIncognito Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

    return redirect(request.META.get('HTTP_REFERER', '/'))  # redirect back to the page


#ext from group by member's
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from chat.models import Group

@login_required
def exit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user in group.members.all():
        group.members.remove(request.user)
    return redirect('group_chat')  # redirect to default group list

from django.http import JsonResponse

@login_required
def group_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = list(group.members.all())

    # Sort so current user comes first
    members.sort(key=lambda m: 0 if m == request.user else 1)

    members_data = []
    for m in members:
        members_data.append({
            "id": m.id,
            "username": m.username,
            "display_name": "You" if m == request.user else m.username
        })
    return JsonResponse({"members": members_data})



# dark_messages.py
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from users.models import TunnelSession

@login_required
def dark_messages_view(request):
    filter_value = request.GET.get('time_filter', 'all')
    page_number = request.GET.get('page', 1)  # Current page number

    tunnels = TunnelSession.objects.all()
    now = timezone.now()

    # Apply filters
    if filter_value == 'today':
        tunnels = tunnels.filter(created_at__date=now.date())
    elif filter_value == 'week':
        week_ago = now - timedelta(days=7)
        tunnels = tunnels.filter(created_at__gte=week_ago)
    elif filter_value == 'month':
        month_ago = now - timedelta(days=30)
        tunnels = tunnels.filter(created_at__gte=month_ago)

    # Update is_active based on expiry
    for tunnel in tunnels:
        if tunnel.expires_at and tunnel.expires_at < now:
            if tunnel.is_active:  # Only update if still marked active
                tunnel.is_active = False
                tunnel.save(update_fields=['is_active'])

    # Prefetch related users & messages
    tunnels = tunnels.prefetch_related(
        'messages__sender__userprofile',
        'messages__receiver__userprofile'
    ).select_related(
        'initiator__userprofile',
        'recipient__userprofile'
    )

    # Pagination: 5 per page
    paginator = Paginator(tunnels, 5)
    page_obj = paginator.get_page(page_number)

    return render(request, 'DASHBOARD/newcode/html/DarkMessages.html', {
        'page_obj': page_obj,
        'filter_value': filter_value
    })




import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

@login_required
@csrf_exempt
def verify_admin_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user and user.is_active and user.is_staff and user.is_superuser:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})
    return JsonResponse({"success": False})


@login_required
def privatemessages(request):
    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html')

@login_required
def groupchats(request):
    return render(request, 'DASHBOARD/newcode/html/GroupMessages.html')

@login_required
def darkmessages(request):
    return render(request, 'DASHBOARD/newcode/html/DarkMessages.html')

@login_required
def reportemessages(request):
    return render(request, 'DASHBOARD/newcode/html/ReportedMessages.html')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from dashboard.models import AuditLog, PrivacySetting, ManageMember  # import your status model
from dashboard.forms import AddAdminForm

@login_required
def privacydash(request):
    # Count all active admins
    active_admins = User.objects.filter(
        is_active=True, 
        is_staff=True, 
        is_superuser=True
    )
    admin_count = active_admins.count()

    # Get last login info
    last_login_info = None
    if active_admins.exists():
        last_admin = active_admins.order_by('-last_login').first()
        if last_admin and last_admin.last_login:
            minutes_ago = int((now() - last_admin.last_login).total_seconds() // 60)
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
            last_login_info = f"{minutes_ago} mins ago from {ip_address}"
        else:
            last_login_info = "No recent login data"
    else:
        last_login_info = "No active admins"

    # Today’s date
    today = now().date()

    # Count today's logins
    login_entries_today = AuditLog.objects.filter(
        action='login',
        created_at__date=today
    ).count()

    # Count critical actions (placeholder)
    critical_actions = AuditLog.objects.filter(
        action='critical',
        created_at__date=today
    ).count()

    # --- Handle Add Admin form submission ---
    if request.method == "POST" and "add_admin" in request.POST:
        form = AddAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('privacydash')  # reload dashboard after adding
    else:
        form = AddAdminForm()

    # Password strength check
    admin_user = User.objects.filter(is_superuser=True).first()
    password_strength = check_password_strength(admin_user.password) if admin_user else None
    privacy_settings, _ = PrivacySetting.objects.get_or_create(id=1)

    # --- NEW: Admins list for table ---
    admins_list = []

    allowed_roles = ["Admin", "Moderator", "Member"]

    for user in active_admins:
        member = ManageMember.objects.filter(member=user).first()
        if member:
            member_status = "Active" if member.status else "Inactive"
            role = member.role if member.role in allowed_roles else "Member"
        else:
            member_status = "Inactive"
            role = "Member"

        profile = UserProfile.objects.filter(user=user).first()
        profile_url = profile.profile_picture.url if profile and profile.profile_picture else f"https://i.pravatar.cc/150?u={user.id}"

        admins_list.append({
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "last_active": user.last_login.strftime("%d %b %Y, %H:%M") if user.last_login else "Never",
            "role": role,
            "status": member_status,
            "profile_url": profile_url,
        })

    # --- Handle Admin Update form submission ---
    if request.method == "POST" and "admin_id" in request.POST:
        admin_id = request.POST.get("admin_id")
        name = request.POST.get("name")
        role = request.POST.get("role")
        status_str = request.POST.get("status")

        # Convert status to Boolean
        status = True if status_str == "True" else False

        # Update User table
        user = get_object_or_404(User, id=admin_id)
        user.username = name
        user.save()

        # Update ManageMember table
        member = get_object_or_404(ManageMember, member=user)  # 'member' is your FK to User
        member.role = role
        member.status = status  # now a Boolean
        member.save()

    #update status and role of admins
    if request.method == "POST" and "admin_id" in request.POST:
        admin_id = request.POST.get("admin_id")
        name = request.POST.get("name")
        role = request.POST.get("role")
        status_str = request.POST.get("status")

        # Convert status to Boolean
        status = True if status_str == "True" else False

        # Update User table
        user = get_object_or_404(User, id=admin_id)
        user.username = name

        # Update User flags based on role
        if role == "Admin":
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
        elif role == "Moderator":
            user.is_superuser = False
            user.is_staff = True
            user.is_active = True
        else:  # Member
            user.is_superuser = False
            user.is_staff = False
            user.is_active = True

        user.save()

        # Update or create ManageMember
        member, created = ManageMember.objects.get_or_create(member=user)
        member.role = role
        member.status = status
        member.save()

        return redirect('privacydash')  # reload page
    
    #add admin or other member
    if request.method == "POST" and "add_admin" in request.POST:
        username = request.POST.get("username").strip()
        role = request.POST.get("role")
        status_str = request.POST.get("status")

        # Convert status to boolean
        status = True if status_str == "True" else False

        # Check if the user already exists
        user, created = User.objects.get_or_create(username=username)

        # Set flags based on role
        if role == "Admin":
            user.is_superuser = True
            user.is_staff = True
        elif role == "Moderator":
            user.is_superuser = False
            user.is_staff = True
        else:  # Member
            user.is_superuser = False
            user.is_staff = False

        # Apply status
        user.is_active = status
        user.save()

        # Update or create ManageMember record
        manage_member, created = ManageMember.objects.get_or_create(member=user)
        manage_member.role = role
        manage_member.status = status
        manage_member.save()

        return redirect("privacydash")


    context = {
        "admin_count": admin_count,
        "last_login_info": last_login_info,
        "login_entries_today": login_entries_today,
        "critical_actions": critical_actions,
        "admin_user": admin_user,
        "password_strength": password_strength,
        "privacy_settings": privacy_settings,
        "admins_list": admins_list,
        "add_admin_form": form,
    }

    return render(request, 'DASHBOARD/newcode/html/PrivacyDash.html', context)


#password_check
import re

@login_required
def check_password_strength(password: str) -> str:
    if not password:
        return "weak"

    length = len(password)
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"\W", password))

    if length >= 8 and has_upper and has_lower and has_digit and has_symbol:
        return "strong"
    elif length >= 8 and ((has_upper or has_lower) and has_digit):
        return "medium"
    else:
        return "weak"


#update admin username and password
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect

@login_required
def update_admin_credentials(request):
    if request.method == "POST":
        user = User.objects.filter(is_superuser=True).first()
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username:
            user.username = username
        if password:
            user.password = make_password(password)

        user.save()
        return redirect("privacydash")

#update session timeout
@login_required
def update_session_timeout(request):
    if request.method == "POST":
        timeout = request.POST.get("session_timeout")
        if timeout:
            profile = request.user.userprofile
            profile.session_timeout = int(timeout)
            profile.save()
        return redirect("privacydash")

#Messagecontent
from dashboard.models import PrivacySetting
# dashboard/views.py
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from dashboard.models import PrivacySetting

@login_required
def update_message_access(request):
    if request.method == "POST":
        selected_value = request.POST.get("message_access", "restricted")

        # Ensure one row exists
        setting, created = PrivacySetting.objects.get_or_create(id=1)
        setting.message_access = selected_value
        setting.save()

        # If it’s an AJAX call, return JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "status": setting.message_access})

        # Otherwise redirect back to the dashboard
        return HttpResponseRedirect(reverse("privacydash"))

    return JsonResponse({"success": False}, status=400)


#toggle to export files
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def toggle_export_permission(request):
    if request.method == "POST":
        data = json.loads(request.body)
        allow_export = data.get("allow_export", False)
        settings, _ = PrivacySetting.objects.get_or_create(id=1)
        settings.allow_export = allow_export
        settings.save()
        return JsonResponse({"success": True, "allow_export": allow_export})
        


@login_required
def manageposts(request):
    return render(request, 'DASHBOARD/newcode/html/ManagePost.html')

@login_required
def useractivity(request):
    return render(request, 'DASHBOARD/newcode/html/UserActivity.html')

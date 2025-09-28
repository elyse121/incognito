from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q

from .models import Message, GroupChat, TunnelMessage
from users.models import TunnelSession


# ------------------ GROUP CHAT ------------------


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Group, GroupChat
from django.contrib.auth.models import User

@login_required
def group_chat_view(request, group_name=None):
    if not group_name:
        # Redirect to a default group or show an error
        first_group = Group.objects.first()
        if first_group:
            return redirect('group_chat', group_name=first_group.name)
        else:
            return render(request, "group_chat.html", {"messages": [], "group": None})

    group = get_object_or_404(Group, name=group_name)

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            GroupChat.objects.create(group=group, sender=request.user, message=message)
            return redirect('group_chat', group_name=group.name)

    messages = GroupChat.objects.filter(group=group).order_by("timestamp")

    return render(request, "group_chat.html", {"messages": messages, "group": group})

#exit group view
from django.contrib import messages

@login_required
def exit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    if user in group.members.all():
        group.members.remove(user)
        messages.success(request, f'You have exited {group.name}')
    return redirect('group_chat')  # Redirect to group list or first group



from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Max
from django.contrib.auth.decorators import login_required
from .models import Group, GroupChat

@login_required
def group_chat_view(request, group_name=None):
    """
    Show all groups where user is a member.
    If group_name is provided, display that group's messages.
    """
    user = request.user

    # Only groups where the logged-in user is a member
    groups = (
        Group.objects.filter(members=user)
        .annotate(
            membersCount=Count('members', distinct=True),
            lastActivity=Max('messages__timestamp')
        )
        .prefetch_related('members', 'messages', 'creator')
    )

    if not group_name:
        # If no group_name in URL, redirect to the first group the user belongs to
        first_group = groups.first()
        if first_group:
            return redirect('group_chat', group_name=first_group.name)
        else:
            # User has no groups
            return render(request, "group_chat.html", {
                "messages": [],
                "group": None,
                "groups": groups
            })

    # Ensure user belongs to this group
    group = get_object_or_404(Group, name=group_name, members=user)

    # Handle new message
    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            GroupChat.objects.create(group=group, sender=user, message=message)
            return redirect('group_chat', group_name=group.name)

    # Fetch all messages in this group
    messages = GroupChat.objects.filter(group=group).order_by("timestamp")

    return render(request, "group_chat.html", {
        "messages": messages,
        "group": group,
        "groups": groups
    })



@login_required
def redirect_to_user5_chat(request):
    user5 = get_object_or_404(User, id=5)
    return redirect('chat', room_name=user5.username)


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'user_profile.html', {'profile_user': user})


# ------------------ PRIVATE CHAT ------------------

@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 
    users = User.objects.exclude(id=request.user.id)

    # ✅ Handle sending new messages (text or media)
    if request.method == "POST":
        content = request.POST.get("content", "")
        media = request.FILES.get("media", None)

        if content or media:
            receiver = get_object_or_404(User, username=room_name)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content if content else None,
                media=media if media else None
            )
        return redirect("chat", room_name=room_name)

    # ✅ Fetch chat history
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    chats = chats.order_by('timestamp')

    # ✅ Build sidebar last messages
    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp.timestamp() if x['last_message'] else 0,
        reverse=True
    )

    show_welcome = room_name == 'index'
    special_message = 'Welcome to the Chatter Room!' if room_name == 'chatter' else None

    context = {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'show_welcome': show_welcome,
        'special_message': special_message,
    }
    return render(request, 'chat.html', context)



# ------------------ SECURE TUNNEL CHAT ------------------

@login_required
def tunnel_chat_view(request, chat_room_id):
    """Render tunnel chat room + load messages"""
    tunnel = get_object_or_404(TunnelSession, chat_room_id=chat_room_id, is_active=True)

    if request.user not in [tunnel.initiator, tunnel.recipient]:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    other_user = tunnel.recipient if request.user == tunnel.initiator else tunnel.initiator

    return render(request, "tunnel_chat.html", {
        "chat_room_id": chat_room_id,
        "tunnel": tunnel,
        "other_user": other_user,
    })


@login_required
def send_tunnel_message(request, chat_room_id):
    """AJAX endpoint to send a tunnel message"""
    if request.method == "POST":
        tunnel = get_object_or_404(TunnelSession, chat_room_id=chat_room_id, is_active=True)

        if request.user not in [tunnel.initiator, tunnel.recipient]:
            return JsonResponse({'success': False, 'error': 'Access denied'})

        content = request.POST.get("content")
        if not content:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})

        receiver = tunnel.recipient if request.user == tunnel.initiator else tunnel.initiator

        msg = TunnelMessage.objects.create(
            tunnel=tunnel,
            sender=request.user,
            receiver=receiver,
            content=content
        )

        return JsonResponse({
            "success": True,
            "sender": msg.sender.username,
            "sender_id": msg.sender.id,
            "receiver": msg.receiver.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M:%S"),
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def fetch_messages(request, chat_room_id):
    """AJAX endpoint to fetch all tunnel messages"""
    try:
        tunnel = TunnelSession.objects.get(chat_room_id=chat_room_id, is_active=True)

        if request.user not in [tunnel.initiator, tunnel.recipient]:
            return JsonResponse({"success": False, "error": "Access denied"})

        # Fetch all historical messages between the two users, regardless of tunnel
        user1 = tunnel.initiator
        user2 = tunnel.recipient
        messages = TunnelMessage.objects.filter(
            Q(sender=user1, receiver=user2) |
            Q(sender=user2, receiver=user1)
        ).order_by('timestamp')

        data = [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "sender_id": msg.sender.id,
                "receiver": msg.receiver.username,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tunnel_chat_room_id": msg.tunnel.chat_room_id  # Include for frontend check
            }
            for msg in messages
        ]

        return JsonResponse({"success": True, "messages": data})

    except TunnelSession.DoesNotExist:
        return JsonResponse({"success": False, "error": "Tunnel not found"})
    


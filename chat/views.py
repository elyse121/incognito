from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q

from .models import Message, GroupChat, TunnelMessage
from users.models import TunnelSession


# ------------------ GROUP CHAT ------------------

@login_required
def group_chat_view(request):
    search_query = request.GET.get("search", "")

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            GroupChat.objects.create(sender=request.user, message=message)

    messages = GroupChat.objects.all().order_by("timestamp")

    if search_query:
        messages = messages.filter(Q(message__icontains=search_query))

    return render(request, "group_chat.html", {
        "messages": messages,
        "search_query": search_query
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

    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    chats = chats.order_by('timestamp')

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
    


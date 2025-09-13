from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

import random
import string
import json

from .models import Post, Like, Comment, UserProfile, Memory, TunnelSession, TunnelOTP

# --------------------
# HELPER
# --------------------
def generate_profile_code():
    return (
        random.choice(string.ascii_uppercase) +
        str(random.randint(1, 9)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    )

# --------------------
# GENERAL PAGES
# --------------------
def index_page(request):
    return render(request, 'index.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('posts')
        else:
            messages.error(request, 'Invalid username or password.')
    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'login.html')

@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_code = generate_profile_code()
        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.save()

        send_mail(
            subject="Your Unique Profile Code",
            message=f"Hello {username},\n\nYour profile code is: {user_profile.profile_code}\n\nKeep it safe!",
            from_email="elyseniyonzima202@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, 'Signup successful! A profile code has been sent to your email.')
        return redirect('login')

    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'signup.html')

@login_required
def home_page(request):
    return render(request, 'chat.html')

# --------------------
# POSTS
# --------------------
@login_required
def posts_page(request):
    posts = Post.objects.all().order_by('-created_at')
    user_liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    return render(request, 'posts.html', {'posts': posts, 'user_liked_post_ids': user_liked_post_ids})

@login_required
def new_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        photo = request.FILES.get('photo')

        if photo:
            fs = FileSystemStorage()
            filename = fs.save(photo.name, photo)
            Post.objects.create(author=request.user, title=title, content=content, photo=filename)
        else:
            Post.objects.create(author=request.user, title=title, content=content)

        return redirect('posts')
    return render(request, 'new_post.html')

@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_obj, created = Like.objects.get_or_create(post=post, user=request.user)
    liked = created
    if not created:
        like_obj.delete()
        liked = False
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_content = request.POST.get('comment')
        if comment_content:
            Comment.objects.create(post=post, content=comment_content, user=request.user)
        return redirect('posts')

# --------------------
# MEMORIES / SOULS
# --------------------
@login_required
def souls_tunnel(request):
    memories = Memory.objects.all().order_by('-created_at')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        memories_data = [{
            'id': m.id,
            'name': m.name,
            'image_url': m.image.url,
            'caption': m.caption,
            'created_at': m.created_at.strftime("%b %d, %Y %I:%M %p")
        } for m in memories]
        return JsonResponse({'memories': memories_data})
    return render(request, 'souls.html', {'memories': memories})

@login_required
@require_POST
def add_memory(request):
    name = request.POST.get('name')
    caption = request.POST.get('caption')
    image = request.FILES.get('image')
    if not all([name, caption, image]):
        return JsonResponse({'status': 'error', 'message': 'All fields are required'})
    memory = Memory.objects.create(user=request.user, name=name, caption=caption, image=image)
    return JsonResponse({
        'status': 'success',
        'memory': {
            'id': memory.id,
            'name': memory.name,
            'image_url': memory.image.url,
            'caption': memory.caption,
            'created_at': memory.created_at.strftime("%b %d, %Y %I:%M %p")
        }
    })

@login_required
def go_to_souls(request):
    return redirect('souls-tunnel')

# --------------------
# CHAT REDIRECT
# --------------------
@login_required
def go_to_chat_with_user5(request):
    user5 = get_object_or_404(User, id=5)
    return redirect('chat', room_name=user5.username)

# --------------------
# PRIVATE TUNNEL
# --------------------
@login_required
def private_tunnel(request):
    return render(request, 'private_tunnel.html')

@login_required
@require_POST
@csrf_exempt
def initiate_tunnel(request):
    try:
        data = json.loads(request.body)
        recipient_username = data.get('recipient')
        recipient = User.objects.filter(username=recipient_username).first()
        if not recipient:
            return JsonResponse({'success': False, 'error': 'User not found'})
        if recipient == request.user:
            return JsonResponse({'success': False, 'error': 'Cannot chat with yourself'})

        tunnel = TunnelSession.objects.create(
            initiator=request.user,
            recipient=recipient,
            expires_at=timezone.now() + timedelta(minutes=30)
        )

        otp = TunnelOTP.objects.create(tunnel_session=tunnel)

        send_mail(
            subject="Private Tunnel Access Code",
            message=f"Hello {recipient.username},\n{request.user.username} wants to chat with you.\nOTP: {otp.otp_code}\nValid for 5 minutes.",
            from_email="elyseniyonzima202@gmail.com",
            recipient_list=[recipient.email],
            fail_silently=False,
        )

        return JsonResponse({'success': True, 'tunnel_id': tunnel.tunnel_id, 'chat_room_id': tunnel.chat_room_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
@csrf_exempt
def verify_tunnel_otp(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        otp_code = str(data.get('otp')).strip()
        tunnel_id = data.get('tunnel_id')

        # Get the tunnel regardless of initiator or recipient
        tunnel = TunnelSession.objects.get(tunnel_id=tunnel_id)

        # Check if the logged-in user is part of this tunnel
        if request.user not in [tunnel.initiator, tunnel.recipient]:
            return JsonResponse({'success': False, 'error': 'Access denied'})

        # Get the latest unused OTP
        otp_obj = tunnel.otps.filter(is_used=False).latest('created_at')

        if not otp_obj or not otp_obj.is_valid():
            return JsonResponse({'success': False, 'error': 'OTP expired or invalid'})

        if otp_obj.otp_code != otp_code:
            return JsonResponse({'success': False, 'error': 'Invalid OTP code'})

        otp_obj.is_used = True
        otp_obj.save()

        tunnel.is_active = True
        tunnel.save()

        return JsonResponse({'success': True, 'chat_room_id': tunnel.chat_room_id})

    except TunnelSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tunnel not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def tunnel_chat(request, chat_room_id):
    """Render the private chat room"""
    try:
        tunnel_session = TunnelSession.objects.get(
            chat_room_id=chat_room_id,
            is_active=True
        )

        if request.user not in [tunnel_session.initiator, tunnel_session.recipient]:
            return JsonResponse({'success': False, 'error': 'Access denied'})

        other_user = tunnel_session.recipient if tunnel_session.initiator == request.user else tunnel_session.initiator

        # Use your existing template name
        return render(request, 'tunner_chat.html', {
            'chat_room_id': chat_room_id,
            'other_user': other_user,
            'tunnel_id': tunnel_session.tunnel_id
        })

    except TunnelSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tunnel not found or inactive'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import random
import string
import json

from .models import Post, Like, Comment, UserProfile, Memory, TunnelSession, TunnelOTP

# Helper function (already in your code)
def generate_profile_code():
    return (
        random.choice(string.ascii_uppercase) +
        str(random.randint(1, 9)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    )

# Modified signup view
def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return render(request, 'signup.html')

        # Create user and profile
        user = User.objects.create_user(username=username, email=email, password=password1)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_code = generate_profile_code()
        user_profile.verification_token = user_profile.generate_verification_token()
        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.save()

        # Send email with profile code and verification link
        verification_link = f"http://127.0.0.1:8000/verify/?token={user_profile.verification_token}"
        send_mail(
            subject="Verify Your Best Friends Portal Account",
            message=f"Hello {username},\n\nYour profile code is: {user_profile.profile_code}\n\nPlease verify your email by clicking this link: {verification_link}\n\nThis link expires in 30 minutes.",
            from_email="elyseniyonzima202@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # Return JSON for AJAX to show "waiting" state
        return JsonResponse({'success': True, 'message': 'Please check your email to verify your account.'})

    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'signup.html')

# New view for email verification
def verify_email(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Invalid verification link.')
        return render(request, 'verify.html')

    try:
        user_profile = UserProfile.objects.get(verification_token=token, is_verified=False)
        user_profile.is_verified = True
        user_profile.verification_token = None  # Clear token after use
        user_profile.save()
        messages.success(request, 'Email verified! You can now log in.')
        return render(request, 'verify.html')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'verify.html')

# Modified login view to check verification
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            user_profile = UserProfile.objects.get(user=user)
            if not user_profile.is_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return render(request, 'login.html')
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('posts')
        else:
            messages.error(request, 'Invalid username or password.')
    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'login.html')

# ... (rest of your views.py remains unchanged)


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
from chat.models import Message

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

"""def login_page(request):
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
    return render(request, 'login.html')"""

    # --- LOGIN ---
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            # Check if banned
            if getattr(user, 'is_banned', False):
                messages.error(request, "Your account is banned.")
                return redirect('banned_account_page')

            # Check if user is active
            if user.is_active:
                login(request, user)
                messages.success(request, 'Login successful!')

                # Redirect based on permissions
                if user.is_active and user.is_staff and user.is_superuser:
                    return redirect('dashindex')   # Admin dashboard
                else:
                    return redirect('posts')       # Normal user page
            else:
                messages.error(request, "This account is inactive. Please contact admin.")
        else:
            messages.error(request, 'Invalid username or password.')

        # Modified login view to check verification
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
    
    # Already logged-in users
    if request.user.is_authenticated:
        if getattr(request.user, 'is_banned', False):
            messages.error(request, "Your account is banned.")
            return redirect('banned_account_page')

        if request.user.is_active:
            return redirect('dashindex' if request.user.is_staff and request.user.is_superuser else 'index')
        else:
            messages.error(request, "Your account is inactive. Please contact admin.")

    return render(request, 'login.html')

@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

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
# SIGNUP + VERIFICATION
# --------------------
def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        # Password check
        if password1 != confirm_password:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": "Passwords do not match"})
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        # Email uniqueness check
        if User.objects.filter(email=email).exists():
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": "Email is already in use"})
            messages.error(request, 'Email is already in use.')
            return render(request, 'signup.html')

        # Create user + profile
        user = User.objects.create_user(username=username, email=email, password=password1)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_code = generate_profile_code()
        user_profile.verification_token = user_profile.generate_verification_token()
        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.save()

        # Build verification link
        verification_link = f"http://127.0.0.1:8000/verify/?token={user_profile.verification_token}"

        # Send email
        send_mail(
            subject="Verify Your Best Friends Portal Account",
            message=(
                f"Hello {username},\n\n"
                f"Your profile code is: {user_profile.profile_code}\n\n"
                f"Please verify your email by clicking this link: {verification_link}\n"
                f"This link expires in 30 minutes."
            ),
            from_email="elyseniyonzima202@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # Response (Ajax vs normal form)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': True, 'message': 'Please check your email to verify your account.'})

        messages.success(request, 'Signup successful! Please check your email to verify your account.')
        return redirect('login')

    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'signup.html')


def verify_email(request):
    """Handle email verification"""
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Invalid verification link.')
        return render(request, 'verify.html')

    try:
        user_profile = UserProfile.objects.get(verification_token=token, is_verified=False)
        user_profile.is_verified = True
        user_profile.verification_token = None  # expire token
        user_profile.save()
        messages.success(request, 'Email verified! You can now log in.')
        return render(request, 'verify.html')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'verify.html')


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
"""def login_page(request):
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
    return render(request, 'login.html')"""

# ... (rest of your views.py remains unchanged)

import requests  # Add this at the top of your file

@login_required
@require_POST
def unlock_archived_messages(request, chat_room_id):
    """
    Verify user's profile code and allow access to archived messages.
    If the code is wrong, email the account owner with intruder info including country and region.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        entered_code = data.get("profile_code", "").strip()

        if not entered_code:
            return JsonResponse({"success": False, "error": "Profile code is required."})

        # Get current user's profile
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.profile_code != entered_code:
            # --- Collect intruder info ---
            ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown UA')
            referer = request.META.get('HTTP_REFERER', 'Unknown referer')
            accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'Unknown language')
            attempt_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            page = request.path

            # --- Get country and region from IP ---
            try:
                response = requests.get(f'https://ipinfo.io/{ip}/json')
                geo_data = response.json()
                country = geo_data.get('country', 'Unknown')
                region = geo_data.get('region', 'Unknown')
                city = geo_data.get('city', 'Unknown')
                org = geo_data.get('org', 'Unknown')  # ISP / Org info
            except:
                country = region = city = org = 'Unknown'

            # --- Send email to account owner ---
            account_owner_email = request.user.email
            subject = "⚠️ Intruder Alert: Wrong Profile Code Attempt"
            text_content = (
                f"A wrong profile code was entered on your account!\n\n"
                f"Username: {request.user.username}\n"
                f"IP Address: {ip}\n"
                f"Country: {country}\n"
                f"Region: {region}\n"
                f"City: {city}\n"
                f"ISP / Org: {org}\n"
                f"Browser / Device: {user_agent}\n"
                f"Page: {page}\n"
                f"Referer: {referer}\n"
                f"Language: {accept_lang}\n"
                f"Time: {attempt_time}\n"
                f"Entered Code: {entered_code}\n\n"
                f"If this wasn't you, please secure your account immediately."
            )
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(to right, #d32f2f, #b71c1c);
            padding: 20px;
            text-align: center;
            color: white;
        }}
        .alert-icon {{
            font-size: 40px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 25px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin: 20px 0;
        }}
        .info-item {{
            padding: 12px;
            background: #f5f5f5;
            border-radius: 6px;
            border-left: 3px solid #d32f2f;
        }}
        .label {{
            font-weight: bold;
            color: #d32f2f;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .warning {{
            background: #ffebee;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            border: 1px solid #ffcdd2;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 15px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}
        @media (max-width: 480px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="alert-icon">⚠️</div>
            <h1>Security Alert: Unauthorized Access Attempt</h1>
        </div>
        
        <div class="content">
            <p>We detected an attempt to access your account using an incorrect profile code.</p>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="label">Username</div>
                    <div>{request.user.username}</div>
                </div>
                <div class="info-item">
                    <div class="label">IP Address</div>
                    <div>{ip}</div>
                </div>
                <div class="info-item">
                    <div class="label">Location</div>
                    <div>{city}, {region}, {country}</div>
                </div>
                <div class="info-item">
                    <div class="label">ISP/Organization</div>
                    <div>{org}</div>
                </div>
                <div class="info-item">
                    <div class="label">Time of Attempt</div>
                    <div>{attempt_time}</div>
                </div>
                <div class="info-item">
                    <div class="label">Entered Code</div>
                    <div>{entered_code}</div>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <div class="label">Browser/Device</div>
                    <div>{user_agent}</div>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <div class="label">Page Accessed</div>
                    <div>{page}</div>
                </div>
            </div>
            
            <div class="warning">
                <h3 style="margin-top: 0; color: #d32f2f;">Immediate Action Recommended</h3>
                <p>If you did not attempt to access your account, please take the following steps immediately:</p>
                <ol>
                    <li>Change your password</li>
                    <li>Review your account activity</li>
                    <li>Enable two-factor authentication if available</li>
                    <li>Contact support if you need assistance</li>
                </ol>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated security alert. Please do not reply to this message.</p>
            <p>© {timezone.now().year} Your Company Name. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

            from django.core.mail import EmailMultiAlternatives
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email="elyseniyonzima202@gmail.com",
                to=[account_owner_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            return JsonResponse({"success": False, "error": "Invalid profile code."})

        # Correct code: unlock messages
        request.session[f"unlocked_{chat_room_id}"] = True
        return JsonResponse({"success": True, "message": "Archived messages unlocked."})

    except UserProfile.DoesNotExist:
        return JsonResponse({"success": False, "error": "Profile not found."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def fetch_messages(request, chat_room_id):
    # get messages for this chat room (example, adapt to your model)
    messages_qs = Message.objects.filter(chat_room_id=chat_room_id).order_by("timestamp")
    unlocked = request.session.get(f"unlocked_{chat_room_id}", False)

    messages_data = []
    for msg in messages_qs:
        messages_data.append({
            "id": msg.id,
            "sender": msg.sender.username,
            "sender_id": msg.sender.id,
            "content": msg.content if unlocked else "[Archived Content]",
            "timestamp": msg.timestamp.isoformat(),
        })

    return JsonResponse({"success": True, "messages": messages_data})


#banned accounts
def banned_account_page(request):
    return render(request, "BannedAccount.html")

def unbann_accounts(request):
    return render(request, 'account_unbanned.html')

def account_banned(request):
    return render(request, 'account_banned.html')




from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from dashboard.models import ManageMember

@require_POST
def ban_user(request, member_id):
    member = get_object_or_404(ManageMember, id=member_id)
    user = member.member

    member.status = False
    member.save(update_fields=["status"])

    # Kill active sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user.id) == str(data.get('_auth_user_id')):
            session.delete()

    # Email notification
    subject = "Your Account Has Been Banned"
    html_message = render_to_string('account_banned.html', {'user': user})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email],
              html_message=html_message)

    return JsonResponse({"success": True, "new_status": member.status})


@require_POST
def unban_user(request, member_id):
    member = get_object_or_404(ManageMember, id=member_id)
    user = member.member

    member.status = True
    member.save(update_fields=["status"])

    subject = "Your Account Has Been Reactivated"
    html_message = render_to_string('account_unbanned.html', {'user': user})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email],
              html_message=html_message)

    return JsonResponse({"success": True, "new_status": member.status})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from dashboard.models import Notification

def banned_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message_content = request.POST.get('message')
        
        # Get the banned user (you might need to adjust this logic)
        # This assumes the user is logged in even when banned
        if request.user.is_authenticated:
            sender = request.user
        else:
            # If user is not logged in, you might need to get the user by email
            # or create a placeholder user. Adjust based on your needs.
            try:
                sender = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a notification without a user if needed
                sender = None
        
        # Create the notification
        if sender:
            Notification.objects.create(
                sender=sender,
                message=message_content,
                email=email
            )
            messages.success(request, 'Your message has been sent to the admin.')
        else:
            # Handle case where we can't find a user
            # You might want to log this or handle differently
            messages.error(request, 'There was an error sending your message.')
        
        return redirect('thank_you')
    
    return render(request, 'BannedAccount.html')


def thank_you(request):
    return render(request, 'thank_you.html')

def unbann_accounts(request):
    return render(request, 'account_unbanned.html')

def account_banned(request):
    return render(request, 'account_banned.html')
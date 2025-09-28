"""# forms.py
from django import forms
from dashboard.models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['email', 'message']  # Include email and message fields
"""

from django import forms
from django.contrib.auth.models import User
from .models import ManageMember

ROLE_CHOICES = [
    ('Admin', 'Admin'),
    ('Moderator', 'Moderator'),
    ('Analyst', 'Analyst'),
]

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
]

class AddAdminForm(forms.ModelForm):
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = ManageMember
        fields = ['member', 'role', 'status']

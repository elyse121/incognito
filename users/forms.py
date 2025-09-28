# forms.py
from django import forms
from dashboard.models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['email', 'message']  # Include email and message fields

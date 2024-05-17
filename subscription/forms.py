# accounts/forms.py
from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'zip_code', 'country', 'comment'] 
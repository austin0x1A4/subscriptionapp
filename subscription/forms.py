from django import forms
from .models import InvestmentModel
from django.forms import DateInput

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = InvestmentModel
        fields = ['investment_amount', 'comments', 'start_date', 'investment_duration']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
        }
class ContactForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

class ContactFormAuthenticated(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
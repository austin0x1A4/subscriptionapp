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

from django import forms
from .models import InvestmentModel
from django.forms import DateInput

class InvestmentForm(forms.ModelForm):
    
    class Meta:
        model = InvestmentModel
        fields = '__all__'
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
        }
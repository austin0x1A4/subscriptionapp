from django import forms

class UploadFileForm(forms.Form):
    INDUSTRY_CHOICES = [
        ('Communications', 'Communications'),
        ('Consumers', 'Consumers'),
        ('Energy', 'Energy'),
        ('Financials', 'Financials'),
        ('Healthcare', 'Healthcare'),
        ('Industrials', 'Industrials'),
        ('Information Technology', 'Information Technology'),
        ('Materials', 'Materials'),
        ('Real Estate', 'Real Estate'),
        ('Utilities', 'Utilities'),
    ]
    file = forms.FileField()
    industry = forms.ChoiceField(choices=INDUSTRY_CHOICES)

from django import forms
PERIODS = (
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('half-yearly', 'Half-Yearly'),
    ('yearly', 'Yearly'),
)
class StockForm(forms.Form):
    symbol = forms.CharField(label='Enter stock symbol', max_length=100)

class CompareForm(forms.Form):
    symbols = forms.CharField(label='Enter stocks to compare', max_length=100)
    period = forms.ChoiceField(choices=PERIODS, label='Select time period')
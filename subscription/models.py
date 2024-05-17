from django.db import models

DURATION_CHOICES = [
    ('1y', '1 year'),
    ('2y', '2 years'),
    ('4y', '4 years'),
    ('5y', '5 years'),
    ('6y', '6 years'),
    ('7y', '7 years'),
    ('8y', '8 years'),
    ('9y', '9 years'),
    ('10y', '10 years'),
    
]

class InvestmentModel(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    investment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    investment_duration = models.CharField(max_length=10, choices=DURATION_CHOICES)

    def __str__(self):
        return self.name
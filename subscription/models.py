from django.db import models
import datetime
from django.contrib.auth.models import User
def generate_custom_account_number():
    now = datetime.datetime.now()
    return f"fud{now.strftime('%Y%m%d%H%M%S%f')}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments', db_column='user_id')  # Add this line
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    investment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    investment_duration = models.CharField(max_length=10, choices=DURATION_CHOICES)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=30, default=generate_custom_account_number, editable=False, unique=True)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    
    def __str__(self):
        return self.user.username

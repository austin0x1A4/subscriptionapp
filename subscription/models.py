from django.db import models
from django.contrib.auth.models import User


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
    account_number = models.CharField(max_length=6, unique=True, editable=False)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.account_number:
            last_account = UserProfile.objects.all().order_by('id').last()
            if last_account:
                last_account_number = int(last_account.account_number)
                self.account_number = str(last_account_number + 1).zfill(6)
            else:
                self.account_number = '000001'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user
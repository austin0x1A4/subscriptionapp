# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField



class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = CountryField()
    comment = models.TextField(blank=True)
    is_subscribed = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return f"{self.user.username}'s Subscription"

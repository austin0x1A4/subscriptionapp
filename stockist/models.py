from django.db import models

class IndexPerformance(models.Model):
    name = models.CharField(max_length=255)
    change = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.change} on {self.date}"

class StockPerformance(models.Model):
    name = models.CharField(max_length=255)
    score = models.FloatField()
    change = models.FloatField()
    market_cap = models.BigIntegerField()
    volume = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.score} on {self.date}"
class Company(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
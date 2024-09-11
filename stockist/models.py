from django.db import models

class IndexPerformance(models.Model):
    name = models.CharField(max_length=255)
    change = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.change} on {self.date}"

class Company(models.Model):
    symbol = models.CharField(max_length=255)  # Stock ticker symbol
    company_name = models.CharField(max_length=255)  # Full company name
    industry = models.CharField(max_length=255)  # Industry of the company
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class StockPerformance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Link to Company model
    score = models.FloatField()
    change = models.FloatField()
    market_cap = models.FloatField(null=True, blank=True)
    volume = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.score} on {self.date}"

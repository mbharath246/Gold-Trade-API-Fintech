from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Gold(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available_gold = models.FloatField(default=0)
    available_balance = models.FloatField(default=0)
    transaction_date = models.DateTimeField(auto_now=True)
    last_gold_sell = models.FloatField(default=0)
    total_gold_sell = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # Round values to two decimal places before saving
        self.available_gold = round(self.available_gold, 2)
        self.available_balance = round(self.available_balance, 2)
        self.last_gold_sell = round(self.last_gold_sell, 2)
        self.total_gold_sell = round(self.total_gold_sell, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.name}, Email - {self.user.email} - Gold: {self.available_gold}g, Balance: {self.available_balance} ₹'  
    


class GoldTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('deposit', 'Deposit'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    grams = models.FloatField()
    amount_in_currency = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.02)  # Example 2% commission

    def __str__(self):
        return f"{self.user.name}, Email - {self.user.email} - {self.transaction_type} {self.grams}g on {self.transaction_date.date()}"
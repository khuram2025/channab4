from django.db import models
from django.contrib.auth.models import User
from accounts.models import Farm
from datetime import date
from django.conf import settings


class IncomeCategory(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExpenseCategory(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)  # Add this line
    date = models.DateField(default=date.today)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='invoices/', blank=True, null=True)


    def __str__(self):
        return f"{self.description} - {self.amount} - {self.category}"


class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)  # Add this line
    date = models.DateField(default=date.today)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='invoices/', blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.category}"

from django.contrib import admin

from .models import Expense, ExpenseCategory, Income, IncomeCategory

@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm']
    # Add any other admin options here

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm']
    # Add any other admin options here

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'farm', 'date', 'description', 'amount', 'category', 'milk_payment']
    # Add any other admin options here

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'farm', 'date', 'description', 'amount', 'category', 'salary_transaction']
    # Add any other admin options here
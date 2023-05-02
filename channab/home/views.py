from django.shortcuts import render
from farm_finances.models import Income, Expense
from django.db.models import Sum


def home_view(request):
    total_income = Income.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    status = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'status': status
    }

    return render(request, 'home/index.html', context)

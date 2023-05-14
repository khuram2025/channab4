# views.py
from django.shortcuts import render
from dairy.models import Animal
from farm_finances.models import Income, Expense, IncomeCategory, ExpenseCategory
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import timedelta, date
from django.utils import timezone

@login_required
def home_view(request):
    farm = request.user.farm

    total_income = Income.objects.filter(farm=farm).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(farm=farm).aggregate(Sum('amount'))['amount__sum'] or 0
    status = total_income - total_expense
    

    now = timezone.now()
    default_time_range = now - timedelta(days=30)  # Default: last 30 days
    time_ranges = {
        "last_7_days": now - timedelta(days=7),
        "last_30_days": now - timedelta(days=30),
        "this_month": now.replace(day=1),
        "this_year": now.replace(month=1, day=1),
    }

    # Get time filter from the request
    time_filter = request.GET.get('time_filter', 'last_30_days')
    selected_time_range = time_ranges.get(time_filter, default_time_range)

    income_categories = IncomeCategory.objects.filter(farm=farm)
    expense_categories = ExpenseCategory.objects.filter(farm=farm)
    sex = request.GET.get('sex', 'male')  # default to 'male' if no parameter is provided
    animals = Animal.objects.filter(farm=farm, sex=sex)
    
    male_animals = Animal.objects.filter(farm=farm, sex='male')
    female_animals = Animal.objects.filter(farm=farm, sex='female')


    summary = []
    for category in income_categories:
        total_amount = Income.objects.filter(
            farm=farm,
            category=category,
            date__gte=selected_time_range
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        summary.append({
            "category": category,
            "total_amount": total_amount,
        })

    expense_summary = []
    for category in expense_categories:
        total_amount = Expense.objects.filter(
            farm=farm,
            category=category,
            date__gte=selected_time_range
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        expense_summary.append({
            "category": category,
            "total_amount": total_amount,
        })

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'status': status,
        "summary": summary,
        "time_filter": time_filter,
        "expense_summary": expense_summary,
        'male_animals': male_animals,
        'female_animals': female_animals,
        'animals': animals,
    }

    return render(request, 'home/index.html', context)

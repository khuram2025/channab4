# views.py
from django.shortcuts import render
from dairy.models import Animal, MilkRecord
from farm_finances.models import Income, Expense, IncomeCategory, ExpenseCategory
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
from django.utils import timezone
from django.db.models import Sum, F, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import DecimalField



def main_view(request):
    return render(request, 'home/about-us.html')

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
   
    # Filter by animals belonging to the user's farm
    today_milk_records = MilkRecord.objects.filter(
        animal__farm=farm,
        date=timezone.now().date()
    )

    # Annotate each record with its total_milk
    today_milk_records = today_milk_records.annotate(
    milk_total=(
        Case(When(first_time__isnull=True, then=0), default=F('first_time'), output_field=DecimalField()) +
        Case(When(second_time__isnull=True, then=0), default=F('second_time'), output_field=DecimalField()) +
        Case(When(third_time__isnull=True, then=0), default=F('third_time'), output_field=DecimalField())
        )
    )
    total_milk_today = today_milk_records.aggregate(total_milk=Sum('milk_total'))['total_milk'] or 0






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
        'total_milk_today': total_milk_today,
    }

    return render(request, 'home/index.html', context)

from rest_framework.permissions import IsAuthenticated

class HomeDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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

        time_filter = request.GET.get('time_filter', 'last_30_days')
        selected_time_range = time_ranges.get(time_filter, default_time_range)

        summary = []
        for category in IncomeCategory.objects.filter(farm=farm):
            total_amount = Income.objects.filter(
                farm=farm,
                category=category,
                date__gte=selected_time_range
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            summary.append({
                "category": category.name,  # Assuming you have a name field in your model
                "total_amount": total_amount,
            })

        expense_summary = []
        for category in ExpenseCategory.objects.filter(farm=farm):
            total_amount = Expense.objects.filter(
                farm=farm,
                category=category,
                date__gte=selected_time_range
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            expense_summary.append({
                "category": category.name,  # Assuming you have a name field in your model
                "total_amount": total_amount,
            })

        male_animals = Animal.objects.filter(farm=farm, sex='male')
        female_animals = Animal.objects.filter(farm=farm, sex='female')
        
        # For API purposes, it's more useful to send the count than actual queryset data for males and females
        male_count = male_animals.count()
        female_count = female_animals.count()
        
        animals = Animal.objects.filter(farm=farm)
        animals_serializer = AnimalSerializer(animals, many=True)

        today_milk_records = MilkRecord.objects.filter(
            animal__farm=farm,
            date=timezone.now().date()
        )
        today_milk_records = today_milk_records.annotate(
            milk_total=(
                Case(When(first_time__isnull=True, then=0), default=F('first_time'), output_field=DecimalField()) +
                Case(When(second_time__isnull=True, then=0), default=F('second_time'), output_field=DecimalField()) +
                Case(When(third_time__isnull=True, then=0), default=F('third_time'), output_field=DecimalField())
            )
        )
        total_milk_today = today_milk_records.aggregate(total_milk=Sum('milk_total'))['total_milk'] or 0

        data = {
            'total_income': total_income,
            'total_expense': total_expense,
            'status': status,
            'summary': summary,
            'time_filter': time_filter,
            'expense_summary': expense_summary,
            'male_animals': male_count,
            'female_animals': female_count,
            'animals': animals_serializer.data,
            'total_milk_today': total_milk_today,
        }

        return Response(data)
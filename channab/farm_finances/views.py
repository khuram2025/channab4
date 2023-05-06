from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import  IncomeCategory, ExpenseCategory
from accounts.models import Farm
from .forms import IncomeCategoryForm, ExpenseCategoryForm
from datetime import date
from django.db.models import F


# Other imports and views

@login_required
def income_categories(request):
    farm = request.user.farm
    income_categories = IncomeCategory.objects.filter(farm=farm)

    return render(request, 'farm_finances/income_categories.html', {'farm': farm, 'income_categories': income_categories})

@login_required
def create_income_category(request):
    farm = request.user.farm
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            income_category = form.save(commit=False)
            income_category.farm = farm
            income_category.save()
            return redirect('farm_finances:income_categories')
    else:
        form = IncomeCategoryForm()

    return render(request, 'farm_finances/create_income_category.html', {'form': form, 'farm': farm})

@login_required
def create_expense_category(request):
    farm = request.user.farm
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            expense_category = form.save(commit=False)
            expense_category.farm = farm
            expense_category.save()
            return redirect('farm_finances:expense_categories')
    else:
        form = ExpenseCategoryForm()

    return render(request, 'farm_finances/create_expense_category.html', {'form': form, 'farm': farm})

@login_required
def update_income_category(request, income_category_id):
    farm = request.user.farm
    income_category = get_object_or_404(IncomeCategory, pk=income_category_id, farm=farm)
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST, instance=income_category)
        if form.is_valid():
            form.save()
            return redirect('farm_finances:income_categories')
    else:
        form = IncomeCategoryForm(instance=income_category)
    return render(request, 'farm_finances/update_income_category.html', {'form': form, 'farm': farm, 'income_category': income_category})


@login_required
def update_expense_category(request, expense_category_id):
    farm = request.user.farm
    expense_category = get_object_or_404(ExpenseCategory, pk=expense_category_id, farm=farm)
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=expense_category)
        if form.is_valid():
            form.save()
            return redirect('farm_finances:expense_categories')
    else:
        form = ExpenseCategoryForm(instance=expense_category)
    return render(request, 'farm_finances/update_expense_category.html', {'form': form, 'farm': farm, 'expense_category': expense_category})

@login_required
def delete_income_category(request, pk):
    income_category = get_object_or_404(IncomeCategory, pk=pk, farm=request.user.farm)
    income_category.delete()
    return redirect('farm_finances:income_categories')


@login_required
def delete_expense_category(request, pk):
    expense_category = get_object_or_404(ExpenseCategory, pk=pk, farm=request.user.farm)
    expense_category.delete()
    return redirect('farm_finances:expense_categories')






@login_required
def expense_categories(request):
    farm = request.user.farm
    expense_categories = ExpenseCategory.objects.filter(farm=farm)
    print(expense_categories)

    return render(request, 'farm_finances/expense_categories.html', {'farm': farm, 'expense_categories': expense_categories})


from django.http import JsonResponse



from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, IncomeForm

@login_required
def create_income(request):
    farm = request.user.farm
    if request.method == "POST":
        form = IncomeForm(request.POST, request.FILES)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.farm = farm
            income.save()
            return redirect('farm_finances:income_list')
    else:
        form = IncomeForm()
        today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'farm_finances/create_income.html', {'form': form, 'today': today_str})

@login_required
def update_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    if request.method == "POST":
        form = IncomeForm(request.POST, request.FILES, instance=income)
        if form.is_valid():
            form.save()
            return redirect('farm_finances:income_list')
    else:
        form = IncomeForm(instance=income)
    today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'farm_finances/update_income.html', {'form': form, 'income': income, 'today': today_str})



@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, farm=request.user.farm)
    income.delete()
    return redirect('farm_finances:income_list')


from django.shortcuts import render
from .models import Income



from datetime import timedelta, datetime

@login_required
def income_list(request):
    farm = request.user.farm
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')
    if sort_order == 'asc':
        incomes = Income.objects.filter(farm=farm).order_by(sort_by)
    else:
        incomes = Income.objects.filter(farm=farm).order_by(F(sort_by).desc(nulls_last=True))

    time_filter = request.GET.get('time_filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if time_filter == 'last_7_days':
        start_date = datetime.today() - timedelta(days=7)
        end_date = datetime.today()
    elif time_filter == 'one_month':
        start_date = datetime.today() - timedelta(days=30)
        end_date = datetime.today()
    elif time_filter == 'three_months':
        start_date = datetime.today() - timedelta(days=90)
        end_date = datetime.today()
    elif time_filter == 'one_year':
        start_date = datetime.today() - timedelta(days=365)
        end_date = datetime.today()

    if start_date and end_date:
        incomes = incomes.filter(date__range=(start_date, end_date))

    return render(request, 'farm_finances/income_list.html', {'incomes': incomes, 'farm': farm, 'sort_by': sort_by, 'sort_order': sort_order})


@login_required
def create_expense(request):
    farm = request.user.farm
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.farm = farm
            expense.save()
            return redirect('farm_finances:expense_list')
    else:
        form = ExpenseForm()
    today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'farm_finances/create_expense.html', {'form': form, 'today': today_str})


from django.shortcuts import render
from .models import Expense

@login_required
def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('farm_finances:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'farm_finances/update_expense.html', {'form': form, 'expense': expense, 'today': today_str})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, farm=request.user.farm)
    expense.delete()
    return redirect('farm_finances:expense_list')


from datetime import timedelta, datetime
from django.utils import timezone


@login_required
def expense_list(request):
    farm = request.user.farm
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')

    if sort_order == 'asc':
        expenses = Expense.objects.filter(farm=farm).order_by(sort_by)
    else:
        expenses = Expense.objects.filter(farm=farm).order_by(F(sort_by).desc(nulls_last=True))

    time_filter = request.GET.get('time_filter', 'one_month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if time_filter == 'last_7_days':
        start_date = datetime.today() - timedelta(days=7)
        end_date = datetime.today()
    elif time_filter == 'one_month':
        start_date = datetime.today() - timedelta(days=30)
        end_date = datetime.today()
    elif time_filter == 'three_months':
        start_date = datetime.today() - timedelta(days=90)
        end_date = datetime.today()
    elif time_filter == 'one_year':
        start_date = datetime.today() - timedelta(days=365)
        end_date = datetime.today()

    if start_date and end_date:
        expenses = expenses.filter(date__range=(start_date, end_date))

    return render(request, 'farm_finances/expense_list.html', {'expenses': expenses, 'farm': farm, 'sort_by': sort_by, 'sort_order': sort_order})

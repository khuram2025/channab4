from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import  IncomeCategory, ExpenseCategory
from accounts.models import Farm
from .forms import IncomeCategoryForm, ExpenseCategoryForm
from datetime import date


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
def delete_income_category(request, income_category_id):
    farm = request.user.farm
    income_category = get_object_or_404(IncomeCategory, pk=income_category_id, farm=farm)
    if request.method == 'POST':
        print('Deleting income category:', income_category_id) # Add this line
        income_category.delete()
        return redirect('farm_finances:all_income_categories')
    return redirect('farm_finances:all_income_categories')



@login_required
def delete_expense_category(request, expense_category_id):
    farm = request.user.farm
    expense_category = get_object_or_404(ExpenseCategory, pk=expense_category_id, farm=farm)
    if request.method == 'POST':
        expense_category.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



@login_required
def expense_categories(request):
    farm = request.user.farm
    expense_categories = ExpenseCategory.objects.filter(farm=farm)
    print(expense_categories)

    return render(request, 'farm_finances/expense_categories.html', {'farm': farm, 'expense_categories': expense_categories})


from django.http import JsonResponse


def delete_expense_category(request, farm_id, expense_category_id):
    farm = get_object_or_404(Farm, pk=farm_id)
    expense_category = get_object_or_404(ExpenseCategory, pk=expense_category_id, farm=farm)
    if request.method == 'POST':
        expense_category.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

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
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    if request.method == "POST":
        income.delete()
        return redirect('farm_finances:income_list')
    return render(request, 'farm_finances/delete_income.html', {'income': income})


from django.shortcuts import render
from .models import Income

@login_required
def income_list(request):
    farm = request.user.farm
    incomes = Income.objects.filter(farm=farm).order_by('-date')
    return render(request, 'farm_finances/income_list.html', {'incomes': incomes, 'farm': farm})

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
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        return redirect('farm_finances:expense_list')
    return render(request, 'farm_finances/delete_expense.html', {'expense': expense})

@login_required
def expense_list(request):
    farm = request.user.farm
    expenses = Expense.objects.filter(farm=farm).order_by('-date')
    return render(request, 'farm_finances/expense_list.html', {'expenses': expenses, 'farm': farm})
from django.urls import path
from . import views

app_name = 'farm_finances'

urlpatterns = [
    # Your other URL patterns

    path('income-categories/', views.income_categories, name='income_categories'),
    path('expense-categories/', views.expense_categories, name='expense_categories'),
    path('update-income-category/<int:income_category_id>/', views.update_income_category, name='update_income_category'),
    path('delete-income-category/<int:income_category_id>/', views.delete_income_category, name='delete_income_category'),

    path('create_income/', views.create_income, name='create_income'),
    path('income_list/', views.income_list, name='income_list'),
    path('update_income/<int:income_id>/', views.update_income, name='update_income'),
    path('delete_income/<int:income_id>/', views.delete_income, name='delete_income'),

    path('create_expense/', views.create_expense, name='create_expense'),
    path('expense_list/', views.expense_list, name='expense_list'),
    path('update_expense/<int:expense_id>/', views.update_expense, name='update_expense'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    path('create-income-category/', views.create_income_category, name='create_income_category'),
    path('create-expense-category/', views.create_expense_category, name='create_expense_category'),

   
    path('update_expense_category/<int:expense_category_id>/', views.update_expense_category, name='update_expense_category'),

    
    path('delete_expense_category/<int:expense_category_id>/', views.delete_expense_category, name='delete_expense_category'),

    # Add update and delete URL patterns for income and expense categories
]


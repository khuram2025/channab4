from django.urls import path
from . import views

app_name = 'farm_finances'

urlpatterns = [
    # Your other URL patterns

    path('<int:farm_id>/income-categories/', views.income_categories, name='income_categories'),
    path('<int:farm_id>/expense-categories/', views.expense_categories, name='expense_categories'),
    path('<int:farm_id>/update-income-category/<int:income_category_id>/', views.update_income_category, name='update_income_category'),
    path('<int:farm_id>/delete-income-category/<int:income_category_id>/', views.delete_income_category, name='delete_income_category'),

    path('create_income/<int:farm_id>/', views.create_income, name='create_income'),
    path('income_list/<int:farm_id>/', views.income_list, name='income_list'),
    path('update_income/<int:farm_id>/<int:income_id>/', views.update_income, name='update_income'),
    path('delete_income/<int:farm_id>/<int:income_id>/', views.delete_income, name='delete_income'),

    path('create_expense/<int:farm_id>/', views.create_expense, name='create_expense'),
    path('expense_list/<int:farm_id>/', views.expense_list, name='expense_list'),
    path('update_expense/<int:farm_id>/<int:expense_id>/', views.update_expense, name='update_expense'),
    path('delete_expense/<int:farm_id>/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    path('<int:farm_id>/create-income-category/', views.create_income_category, name='create_income_category'),
    path('<int:farm_id>/create-expense-category/', views.create_expense_category, name='create_expense_category'),

    path('<int:farm_id>/update_income_category/<int:income_category_id>/', views.update_income_category, name='update_income_category'),
    path('<int:farm_id>/update_expense_category/<int:expense_category_id>/', views.update_expense_category, name='update_expense_category'),

    path('<int:farm_id>/delete_income_category/<int:income_category_id>/', views.delete_income_category, name='delete_income_category'),
    path('<int:farm_id>/delete_expense_category/<int:expense_category_id>/', views.delete_expense_category, name='delete_expense_category'),

    # Add update and delete URL patterns for income and expense categories
]

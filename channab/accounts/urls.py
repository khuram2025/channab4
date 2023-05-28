from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profile/', views.user_profile, name='user_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('create_farm_member/', views.create_farm_member, name='create_farm_member'),
    path('edit_member/<int:pk>/', views.edit_member, name='edit_member'),
    path('member/<int:member_id>/', views.member_detail, name='member_detail'),
    path('reset_password/<int:pk>/', views.reset_password, name='reset_password'),
    path('delete_member/<int:pk>/', views.delete_member, name='delete_member'),
    path('farm_member_list/', views.farm_member_list, name='farm_member_list'),
    
    path('member/<int:member_id>/salary/', views.salary_components, name='salary_components'),
    path('member/<int:member_id>/salary/add/', views.add_salary_component, name='add_salary_component'),
    
    path('salary_transactions/', views.salary_transaction_list, name='salary_transaction_list'),
    path('get_salary_components/<int:user_id>/', views.get_salary_components, name='get_salary_components'),
    path('salary_transactions/create/', views.salary_transaction_update, name='salary_transaction_create'),
    path('salary_transactions/update/<int:pk>/', views.salary_transaction_update, name='salary_transaction_update'),
    path('salary_transactions/delete/<int:pk>/', views.salary_transaction_delete, name='salary_transaction_delete'),
    

    path('login/', views.login_view, name='login'),
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('logout/', views.logout_view, name='logout'),
]

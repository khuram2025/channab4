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
    path('delete_member/<int:pk>/', views.delete_member, name='delete_member'),
    path('farm_member_list/', views.farm_member_list, name='farm_member_list'),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/', views.HomeDataAPIView.as_view(), name='api_home'),
    
]

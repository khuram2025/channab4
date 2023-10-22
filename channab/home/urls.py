from django.urls import path
from . import views

app_name = 'home'


urlpatterns = [
    path('', views.home_view, name='home'),
    path('home1', views.main_view, name='main_view'),
    path('services', views.services, name='services'),
    path('api/', views.HomeDataAPIView.as_view(), name='api_home'),
    
]

from django.urls import path
from . import views

app_name = 'dairy'

urlpatterns = [
    # other url patterns
    path('animal-categories/', views.animal_category_list, name='animal_category_list'),
    path('animal-categories/create/', views.animal_category_create, name='animal_category_create'),
    path('animal-categories/<int:pk>/edit/', views.animal_category_edit, name='animal_category_edit'),
    path('animal-categories/<int:pk>/delete/', views.animal_category_delete, name='animal_category_delete'),
]

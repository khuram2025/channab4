from django.urls import path
from . import views

app_name = 'dairy'

urlpatterns = [
    # other url patterns
    path('animal-categories/', views.animal_category_list, name='animal_category_list'),
    path('animal-categories/create/', views.animal_category_create, name='animal_category_create'),
    path('animal-categories/<int:pk>/edit/', views.animal_category_edit, name='animal_category_edit'),
    path('animal-categories/<int:pk>/delete/', views.animal_category_delete, name='animal_category_delete'),

    path('animals/', views.animal_list, name='animal_list'),
    path('animals/create/', views.animal_create, name='animal_create'),
    path('animals/edit/<int:pk>/', views.animal_edit, name='animal_edit'),
    path('animals/delete/<int:pk>/', views.animal_delete, name='animal_delete'),
]

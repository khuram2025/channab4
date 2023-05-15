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
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
     path('animal/<int:pk>/add_family/', views.add_family, name='add_family'),
     path('family/<int:pk>/edit/', views.EditFamilyView.as_view(), name='edit_family'),
     path('family/<int:pk>/delete/', views.DeleteFamilyView.as_view(), name='delete_family'),

    path('animals/create/', views.animal_create, name='animal_create'),
    path('animals/edit/<int:pk>/', views.animal_edit, name='animal_edit'),
    path('animals/<int:pk>/delete/', views.delete_animal, name='delete_animal'),


    path('animal_milk/', views.animal_milk_list, name='animal_milk_list'),
    path('animal_milks/new/', views.animal_milk_new, name='animal_milk_new'),
    path('animal_milks/<int:pk>/edit/', views.animal_milk_edit, name='animal_milk_edit'),
    path('animal_milks/<int:pk>/delete/', views.animal_milk_delete, name='animal_milk_delete'),

    

    path('milk_record/<int:milk_record_id>/edit/', views.edit_milk_record, name='milk_edit'),
    path('milk_record/<int:milk_record_id>/delete/', views.delete_milk_record, name='milk_delete'),

    path('animal/<int:animal_id>/add_milk_record/', views.add_milk_record, name='add_milk_record'),
    path('animal/<int:animal_id>/get_milk_record/<str:date>/', views.get_milk_record, name='get_milk_record'),


    path('animal_weights/', views.animal_weight_list, name='animal_weight_list'),
    path('animal_weights/<int:pk>/', views.animal_weight_detail, name='animal_weight_detail'),
    path('animal_weights/new/<int:pk>/', views.animal_detail_weight_new, name='animal_detail_weight_new'),
    path('animal_weights/new/', views.animal_weight_new, name='animal_weight_new'),
    path('animal_weights/<int:pk>/edit/', views.animal_weight_edit, name='animal_weight_edit'),
    path('animal_weights/<int:pk>/delete/', views.animal_weight_delete, name='animal_weight_delete'),

]

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
    path('animals/create/', views.animal_create, name='animal_create'),
    path('animals/edit/<int:pk>/', views.animal_edit, name='animal_edit'),
    path('animals/delete/<int:pk>/', views.animal_delete, name='animal_delete'),

    path('milk-record', views.MilkRecordListView.as_view(), name='milk-list'),
    path('milk-record/create/', views.MilkRecordCreateUpdateView.as_view(), name='milk-create'),
    path('milk-record/update/<int:pk>/', views.MilkRecordCreateUpdateView.as_view(), name='milk-update'),
    path('milk-record/delete/<int:pk>/', views.MilkRecordDeleteView.as_view(), name='milk-delete'),

    path('milk_record/<int:milk_record_id>/edit/', views.edit_milk_record, name='milk_edit'),
    path('milk_record/<int:milk_record_id>/delete/', views.delete_milk_record, name='milk_delete'),

    path('animal/<int:animal_id>/add_milk_record/', views.add_milk_record, name='add_milk_record'),
    path('animal/<int:animal_id>/get_milk_record/<str:date>/', views.get_milk_record, name='get_milk_record'),

]

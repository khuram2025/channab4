from django.urls import path
from . import views
from .views import AnimalDetailView


app_name = 'dairy_farm'

urlpatterns = [
    path('animals/', views.animal_list, name='animal_list'),
    path('add-animal/', views.add_animal, name='add_animal'),
    path('animal/<int:pk>/', AnimalDetailView.as_view(), name='animal_detail'),
    path('edit-animal/<int:pk>/', views.edit_animal, name='edit_animal'),
    path('delete-animal/<int:pk>/', views.delete_animal, name='delete_animal'),
    path('categories/', views.AnimalCategoryListView.as_view(), name='animalcategory_list'),
    path('categories/create/', views.AnimalCategoryCreateView.as_view(), name='animalcategory_create'),
    path('categories/update/<int:pk>/', views.AnimalCategoryUpdateView.as_view(), name='animalcategory_update'),
    path('categories/delete/<int:pk>/', views.AnimalCategoryDeleteView.as_view(), name='animalcategory_delete'),

    path('animal/<int:animal_id>/add_milk_record/', views.add_milk_record, name='add_milk_record'),
    path('animal/<int:animal_id>/get_milk_record/<str:date>/', views.get_milk_record, name='get_milk_record'),

    path('milk_records/', views.milk_records, name='milk_records'),
    path('milk_records/edit/<int:milk_record_id>/', views.edit_all_milk_record, name='edit_all_milk_record'),
    path('milk_records/delete/<int:milk_record_id>/', views.delete_all_milk_record, name='delete_milk_record'),
    path('milk_record/<int:milk_record_id>/edit/', views.edit_milk_record, name='edit_milk_record'),
    path('milk_records/add/', views.add_milk_record_to_animal, name='add_milk_record_to_animal'),
    path('milk_record/<int:milk_record_id>/delete/', views.delete_milk_record, name='delete_milk_record'),
    path('farm/', views.farm_list, name='farm_list'),
    path('detail/<int:farm_id>/', views.farm_detail, name='farm_detail'),
    path('dairy-farm/detail/<int:farm_id>/add-member/', views.add_member, name='add_member'),
    path('add-member/<int:farm_id>/', views.add_member_page, name='add_member_page'),
    path('add/', views.add_farm, name='add_farm'),
    
    path('edit/<int:farm_id>/', views.edit_farm, name='edit_farm'),

    path('animal/<int:pk>/add_relation/', views.AnimalRelationCreateView.as_view(), name='add_relation'),
    path('animal/relation/<int:pk>/update/', views.AnimalRelationUpdateView.as_view(), name='update_relation'),
    path('animal/relation/<int:pk>/delete/', views.AnimalRelationDeleteView.as_view(), name='delete_relation'),

    path('animal/<int:animal_id>/add_weight/', views.add_weight_record, name='add_weight'),
    path('animal_weight/<int:weight_record_id>/delete/', views.animal_weight_delete_view, name='delete_weight'),

    path('weight/<int:weight_record_id>/edit/', views.edit_weight_record, name='edit_weight'),

  
    
    
]

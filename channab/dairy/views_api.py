from .models import Animal, AnimalWeight
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from .models import AnimalCategory, Animal, Breeding, Customer, MilkPayment, MilkSale
from .forms import AnimalCategoryForm, AnimalForm, AnimalWeightForm, CustomerForm, MilkPaymentForm, MilkRecordForm, MilkSaleForm
from accounts.models import Farm
from .models import MilkRecord, Animal, AnimalWeight
from django.db.models import F
from datetime import timedelta, date
from django.http import JsonResponse
from calendar import monthrange
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.db.models import F, Q, Value, DecimalField
from django.http import HttpResponseForbidden, JsonResponse
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce
from farm_finances.models import IncomeCategory, Income
from django.core.paginator import Paginator
from django.conf import settings
from urllib.parse import urljoin

from django.db.models import Subquery, OuterRef


class AnimalListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        farm = request.user.farm
        animals = Animal.objects.filter(farm=farm).order_by('id')  # Add order_by here
        animals = animals.annotate(latest_weight=Subquery(
            AnimalWeight.objects.filter(animal=OuterRef('pk')).order_by('-date')[:1].values('weight_kg')
        ))
        
        animal_types = dict(Animal.TYPE_CHOICES)
        
        categories = AnimalCategory.objects.filter(Q(farm=farm) | Q(is_site_level=True))

        selected_category_slug = request.GET.get('categorySelect')
        if selected_category_slug:
            animals = animals.filter(category__slug=selected_category_slug)

        animals_by_type = {}
        counts_by_type = {}  
        paginators_by_type = {}
        page_objs_by_type = {}

        selected_type = request.GET.get('type', 'all')  # get the type parameter from the URL
        selected_age_range = request.GET.get('age_range', 'all')  # get the age range parameter from the URL
        # filter the animals based on the selected type
        if selected_type != 'all':
            animals = animals.filter(animal_type=selected_type)
        now = date.today()
        

        min_age = request.GET.get('minAge')
        max_age = request.GET.get('maxAge')
        animal_type = request.GET.get('animalTypeSelect')
        animal_status = request.GET.get('animalStatusSelect')
        is_male = 'maleCheckbox' in request.GET
        is_female = 'femaleCheckbox' in request.GET
        # Filter by min and max age
        if min_age:
            max_age_date = now - timedelta(days=int(min_age)*30)
            animals = animals.filter(dob__lte=max_age_date)
        if max_age:
            min_age_date = now - timedelta(days=int(max_age)*30)
            animals = animals.filter(dob__gte=min_age_date)

        
        # Filter by animal type
        if animal_type and animal_type != 'all':
            animals = animals.filter(animal_type=animal_type)
        # Filter by animal status
        if animal_status and animal_status != 'all':
            animals = animals.filter(status=animal_status)
        # Filter by gender
        if is_male and not is_female:
            animals = animals.filter(sex='male')
        elif is_female and not is_male:
            animals = animals.filter(sex='female')
        # Add paginator and page object for 'all' animals
        paginator_all = Paginator(animals, 10)
        page_number_all = request.GET.get('page')
        page_objs_by_type['all'] = paginator_all.get_page(page_number_all) 
        for animal_type in animal_types:
            animals_of_type = animals.filter(animal_type=animal_type)
            animals_by_type[animal_type] = animals_of_type
            counts_by_type[animal_type] = animals_of_type.count() 
            paginators_by_type[animal_type] = Paginator(animals_of_type, 14)
            page_number = request.GET.get('page')
            page_objs_by_type[animal_type] = paginators_by_type[animal_type].get_page(page_number)
        
        
        animals_data = []
        for animal in animals:
            animal_dict = {
                'id': animal.id,
                'tag': animal.tag,
                'dob': animal.dob,
                'latest_weight': animal.latest_weight,
                'animal_type': animal.animal_type,
                'status': animal.status,
                'sex': animal.sex,
                'category_title': animal.category.title,
                'purchase_cost': animal.purchase_cost,
                'image_url': urljoin(settings.MEDIA_URL, animal.image.url) if animal.image else None
            }
            animals_data.append(animal_dict)
        print("Animals data prepared for response:")
        print(animals_data)

        return Response({'animals': animals_data})


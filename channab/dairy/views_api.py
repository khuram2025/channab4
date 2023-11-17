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
from django.db.models import Sum, Avg
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
from .serializers import AnimalSerializer, MilkRecordSerializer
from rest_framework import status


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
        # print("Animals data prepared for response:")
        # print(animals_data)

        return Response({'animals': animals_data})

class AnimalDetailView(APIView):
   def get(self, request, pk):
        print(f"Request received for animal with pk: {pk}")
        farm = request.user.farm
        try:
            animal = Animal.objects.get(pk=pk, farm=farm)
            serializer = AnimalSerializer(animal)

            # Time filter handling
            time_filter = request.GET.get('time_filter', 'this_month')
            start_date, end_date = self.get_date_range(time_filter)
            print(f"Time filter: {time_filter}, Start Date: {start_date}, End Date: {end_date}")

            # Fetch milk records based on the time filter
            milk_records = MilkRecord.objects.filter(animal=animal, date__range=(start_date, end_date))
            milk_records = milk_records.annotate(total_milk_annotation=F('first_time') + F('second_time') + F('third_time'))

            print(f"Milk Records QuerySet: {milk_records}")
            if not milk_records.exists():
                print("No milk records found for the given time filter.")

            # Aggregations
            totals = milk_records.aggregate(
                total_first_time=Sum('first_time'),
                total_second_time=Sum('second_time'),
                total_third_time=Sum('third_time'),
                total_milk=Sum('total_milk_annotation')  # Use the annotated field
            )

            days = (end_date - start_date).days + 1

            # Calculate average milk per day
            average_milk_per_day = 0
            if totals['total_milk'] is not None and days > 0:
                average_milk_per_day = totals['total_milk'] / days

            # Serialize milk records and prepare response data
            serialized_milk_records = MilkRecordSerializer(milk_records, many=True).data
            response_data = serializer.data
            response_data['milk_records'] = serialized_milk_records
            response_data['totals'] = totals
            response_data['average_milk_per_day'] = average_milk_per_day

            print(f"Serialized data: {serializer.data}")
            return Response(response_data)
        except Animal.DoesNotExist:
            return Response({"error": "Animal not found"}, status=status.HTTP_404_NOT_FOUND)
    
   def get_date_range(self, time_filter):
        today = timezone.now().date()
        if time_filter == 'all':
            start_date = Animal.objects.earliest('dob').dob
            end_date = today
        elif time_filter == 'today':
            start_date = end_date = today
        elif time_filter == 'last_7_days':
            start_date = today - timedelta(days=6)
            end_date = today
        elif time_filter == 'last_30_days':
            start_date = today - timedelta(days=29)
            end_date = today
        elif time_filter == 'last_1_year':
            start_date = today - timedelta(days=364)
            end_date = today
        elif time_filter == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif time_filter == 'custom':
            start_date = request.GET.get('start_date', today.replace(day=1))
            end_date = request.GET.get('end_date', today)
        else:
            start_date = today.replace(day=1)  # Default to this month
            end_date = today
        return start_date, end_date

        
     
        farm = request.user.farm
        try:
            animal = Animal.objects.get(pk=pk, farm=farm)
            serializer = AnimalSerializer(animal)
            print(f"Serialized data: {serializer.data}")
            return Response(serializer.data)
        except Animal.DoesNotExist:
            return Response({"error": "Animal not found"}, status=status.HTTP_404_NOT_FOUND)
        

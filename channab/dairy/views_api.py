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
from django.db.models import Count
from django.conf import settings
from urllib.parse import urljoin
from .serializers import AnimalSerializer, MilkRecordSerializer
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist



from django.db.models import Subquery, OuterRef



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_animals(request):
    try:
        farm = request.user.farm
        animal_type_query = request.query_params.get('type', None)

        if animal_type_query:
            animals = Animal.objects.filter(farm=farm, animal_type__iexact=animal_type_query).order_by('id')
            # print(f"Filtering animals by type: {animal_type_query}, found {animals.count()} animals.")
        else:
            animals = Animal.objects.filter(farm=farm).order_by('id')
            # print(f"Fetching all animals, found {animals.count()} animals.")

        serializer = AnimalSerializer(animals, many=True)
        # print("Serialized data:", serializer.data)

        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "Farm not found for the user"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_animal_types(request):
    try:
        farm = request.user.farm

        # Getting the count of each animal type
        animal_types_with_count = (
            Animal.objects.filter(farm=farm)
            .values('animal_type')
            .annotate(count=Count('animal_type'))
            .order_by('animal_type')
        )

        # print(f"Animal types and counts: {animal_types_with_count}")

        return Response(animal_types_with_count)
    except ObjectDoesNotExist:
        return Response({"error": "Farm not found for the user"}, status=404)    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_milk_records(request, animal_id):
    try:
        milk_records = MilkRecord.objects.filter(animal_id=animal_id).order_by('date')
        serializer = MilkRecordSerializer(milk_records, many=True)
        print("Serialized milk records:", serializer.data)
    
        return Response(serializer.data)
    except MilkRecord.DoesNotExist:
        return Response({"error": "Milk records not found for the specified animal"}, status=404)
    

class AnimalDetailView(APIView):
    def get(self, request, pk):
        print(f"Request received for animal with pk: {pk}")
        farm = request.user.farm
        try:
            animal = Animal.objects.get(pk=pk, farm=farm)
            serializer = AnimalSerializer(animal)

            # Time filter handling
            time_filter = request.GET.get('time_filter', 'this_month')
            start_date, end_date = self.get_date_range(time_filter, request)  # Pass request here
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
                total_milk=Sum('total_milk_annotation')
            )

            # Calculate the number of days in the selected range
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

    # ... rest of your class code ...

    def get_date_range(self, time_filter, request):
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
                start_date_str = request.GET.get('start_date', today.replace(day=1).isoformat())
                end_date_str = request.GET.get('end_date', today.isoformat())

                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
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
        

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

from django.utils.timezone import make_aware
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
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import MilkRecord
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Subquery, OuterRef
from .views import get_date_range
from django.core.serializers.json import DjangoJSONEncoder

from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_total_milk_list(request):
    # Determine the time filter from the request, defaulting to 'this_year'
    time_filter = request.GET.get('filter', 'this_year')
    today = timezone.now().date()
    start_date, end_date = api_get_date_range(time_filter, today)

    
    
    milk_records = (
        MilkRecord.objects.filter(date__range=(start_date, end_date))
        .values('date')  
        .annotate(
            first_time_total=Coalesce(Sum('first_time', output_field=DecimalField()), 0, output_field=DecimalField()),
            second_time_total=Coalesce(Sum('second_time', output_field=DecimalField()), 0, output_field=DecimalField()),
            third_time_total=Coalesce(Sum('third_time', output_field=DecimalField()), 0, output_field=DecimalField()),
        )
        .order_by('date')
    )

    records_list = []
    for record in milk_records:
        date_str = record['date'].strftime('%Y-%m-%d')
        first_time_total = record['first_time_total']
        second_time_total = record['second_time_total']
        third_time_total = record['third_time_total']
        total_milk = first_time_total + second_time_total + third_time_total
        
        # Printing each record with detailed milking times
        print(f"Date: {date_str}, 1st Time: {first_time_total}, 2nd Time: {second_time_total}, 3rd Time: {third_time_total}, Total Milk: {total_milk}")
        
        records_list.append({
            'date': date_str,
            'first_time': first_time_total,
            'second_time': second_time_total,
            'third_time': third_time_total,
            'total_milk': total_milk,
        })

    
    print(f"Sending {len(records_list)} records to API: {records_list}")


    return Response({
        'records': records_list,
        'time_filter': time_filter
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_milk_record(request):
    farm = request.user.farm

    # Print the incoming request data
    print("Received Milk Record Data:\n", request.data)

    serializer = MilkRecordSerializer(data=request.data)

    if serializer.is_valid():
        animal_id = serializer.validated_data.get('animal').id
        date = serializer.validated_data.get('date')

        # Ensure the animal belongs to the user's farm
        if not Animal.objects.filter(id=animal_id, farm=farm).exists():
            return Response({'error': 'Animal not found in your farm.'}, status=status.HTTP_404_NOT_FOUND)

        milk_record = serializer.save()
        return Response(MilkRecordSerializer(milk_record).data, status=status.HTTP_201_CREATED)

    else:  # Log validation errors
        print("Validation Errors:\n", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_filtered_milk_animals(request):
    user = request.user
    animals = Animal.objects.filter(sex='female', animal_type__in=['milking', 'preg_milking'])
    serializer = AnimalSerializer(animals, many=True)
    return Response(serializer.data)

def api_get_date_range(filter_key, today):
    print(f"Received filter key: {filter_key}")
    if filter_key == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif filter_key == 'last_7_days':
        end_date = today
        start_date = today - timedelta(days=7)
    elif filter_key == 'this_month':
        start_date = today.replace(day=1)
        year = today.year
        month = today.month
        # Correctly determine the last day of the month
        if month == 2: #  Special case for February
            last_day = 29 if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else 28
        else:
            next_month = today.replace(day=28) + datetime.timedelta(days=4) 
            last_day = next_month - datetime.timedelta(days=next_month.day) 

        end_date = today.replace(day=last_day)
    else:
        # Default case, can adjust based on requirements
        start_date = today
        end_date = today
    print(f"Calculated date range: Start: {start_date}, End: {end_date}")
    return start_date, end_date



def calculate_totals(milk_records):
    totals = {}
    for record in milk_records:
        # Ensure the date is converted to a string here
        date_str = record['date'].isoformat() if isinstance(record['date'], date) else record['date']
        totals[date_str] = {
            'total_first_time': record['first_time_total'] or 0,
            'total_second_time': record['second_time_total'] or 0,
            'third_time_total': record['third_time_total'] or 0,
            'total_milk': record['total_milk'] or 0,
        }
    return totals



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



from datetime import datetime, timedelta
from django.utils.timezone import make_aware

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_milk_records(request, animal_id):
    filter_option = request.query_params.get('filter', 'This Month')
    custom_start = request.query_params.get('custom_start')  # YYYY-MM-DD
    custom_end = request.query_params.get('custom_end')  # YYYY-MM-DD
    today = datetime.today()

    # Default range (covers entire available data)
    start_date = make_aware(datetime(2000, 1, 1))
    end_date = make_aware(datetime(2099, 12, 31))

    if filter_option == 'This Month':
        start_date = make_aware(datetime(today.year, today.month, 1))
        end_date = make_aware(datetime(today.year, today.month + 1, 1)) - timedelta(days=1)
    elif filter_option == 'Last 7 Days':
        end_date = make_aware(today)
        start_date = end_date - timedelta(days=6)
    elif filter_option == 'Last Year':
        start_date = make_aware(datetime(today.year - 1, 1, 1))
        end_date = make_aware(datetime(today.year, 1, 1)) - timedelta(days=1)
    elif filter_option == 'Custom Range' and custom_start and custom_end:
        start_date = make_aware(datetime.strptime(custom_start, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(custom_end, '%Y-%m-%d'))

    try:
        milk_records = MilkRecord.objects.filter(animal_id=animal_id, date__range=[start_date, end_date]).order_by('date')
        serializer = MilkRecordSerializer(milk_records, many=True)
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
        




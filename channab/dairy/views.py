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

@login_required
def search(request):
    q = request.GET.get('q', '')

    # Get the farm of the logged in user
    user_farm = request.user.farm

    animals = Animal.objects.filter(
        Q(tag__icontains=q) |
        Q(category__title__icontains=q) |
        Q(sex__icontains=q) |
        Q(status__icontains=q),
        farm=user_farm  # Limit search to the user's farm
    )

    data = serializers.serialize('json', animals)
    return JsonResponse(data, safe=False)

@login_required
def animal_category_list(request):
    farm = request.user.farm
    categories = AnimalCategory.objects.filter(farm=farm)
    return render(request, 'dairy/animal_category_list.html', {'categories': categories})


@login_required
def animal_category_create(request):
    farm = get_object_or_404(Farm, admin=request.user)
    if request.method == 'POST':
        form = AnimalCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.farm = farm
            category.save()
            return redirect('dairy:animal_category_list')
    else:
        form = AnimalCategoryForm()
    return render(request, 'dairy/animal_category_form.html', {'form': form})


@login_required
def animal_category_edit(request, pk):
    category = get_object_or_404(
        AnimalCategory, pk=pk, farm__admin=request.user)
    if request.method == 'POST':
        form = AnimalCategoryForm(
            request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('dairy:animal_category_list')
    else:
        form = AnimalCategoryForm(instance=category)
    return render(request, 'dairy/animal_category_form.html', {'form': form})


@login_required
def animal_category_delete(request, pk):
    category = get_object_or_404(
        AnimalCategory, pk=pk, farm__admin=request.user)
    if request.method == 'POST':
        category.delete()
        return HttpResponseRedirect(reverse('dairy:animal_category_list'))
    return render(request, 'dairy/delete.html', {'category': category})

from django.core.paginator import Paginator
# just a comment 
@login_required
def animal_list(request):
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
    
    if request.is_ajax():
        # Convert animals queryset to list of dicts for JSON response
        animals_data = list(animals.values('id', 'name', 'dob', 'latest_weight', 'animal_type'))
        return JsonResponse({'animals': animals_data})
    else:
        return render(request, 'dairy/animal_list.html', {
            'animals': animals, 
            'animals_by_type': animals_by_type, 
            'counts_by_type': counts_by_type, 
            'page_objs_by_type': page_objs_by_type,
            'selected_type': selected_type,
            'selected_age_range': selected_age_range,
            'categories': categories
        })


@login_required
def animal_create(request):
    farm = get_object_or_404(Farm, admin=request.user)
    edit_mode = False
    if request.method == 'POST':
        print("Form submitted")  # Add this line
        form = AnimalForm(request.POST, request.FILES, farm=farm)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.farm = farm
            animal.save()
            return redirect('dairy:animal_list')
        else:
            print(form.errors)  # Add this line to print form errors
    else:
        form = AnimalForm(farm=farm)
    return render(request, 'dairy/animal_form.html', {'form': form, 'edit_mode': edit_mode})




@login_required
def animal_edit(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__admin=request.user)
    edit_mode = True
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('dairy:animal_list')
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'dairy/animal_form.html', {'form': form, 'edit_mode': edit_mode, 'animal': animal })


from django.http import HttpResponseRedirect, JsonResponse

import logging
logger = logging.getLogger(__name__)

@login_required
def animal_detail(request, pk):
    farm = request.user.farm
    animal = get_object_or_404(Animal, pk=pk, farm=farm)

    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')

    if sort_order == 'asc':
        weights = AnimalWeight.objects.filter(animal=animal).select_related('animal').order_by(sort_by)
    else:
        weights = AnimalWeight.objects.filter(animal=animal).select_related('animal').order_by(F(sort_by).desc(nulls_last=True))

    prev_weights = {}
    for weight in weights:
        prev_weight = AnimalWeight.objects.filter(animal=weight.animal, date__lt=weight.date).order_by('-date').first()
        prev_weights[weight.pk] = prev_weight 

    # Assume time_filter is passed as a parameter in the GET request
    time_filter = request.GET.get('time_filter', 'all')

    # Filter MilkRecord instances based on the time_filter
    if time_filter == 'all':
        milk_records = MilkRecord.objects.filter(animal=animal)
    elif time_filter == 'last_day':
        one_day_ago = timezone.now() - timedelta(days=1)
        milk_records = MilkRecord.objects.filter(animal=animal, date__gte=one_day_ago)
    elif time_filter == 'last_7_days':
        seven_days_ago = timezone.now() - timedelta(days=7)
        milk_records = MilkRecord.objects.filter(animal=animal, date__gte=seven_days_ago)
    elif time_filter == 'one_month':
        one_month_ago = timezone.now() - timedelta(days=30)
        milk_records = MilkRecord.objects.filter(animal=animal, date__gte=one_month_ago)
    elif time_filter == 'four_months':
        four_months_ago = timezone.now() - timedelta(days=120)
        milk_records = MilkRecord.objects.filter(animal=animal, date__gte=four_months_ago)
    elif time_filter == 'one_year':
        one_year_ago = timezone.now() - timedelta(days=365)
        milk_records = MilkRecord.objects.filter(animal=animal, date__gte=one_year_ago)

    # Summarize milk_records to obtain total quantities
    total_first_time = milk_records.aggregate(Sum('first_time'))['first_time__sum']
    total_second_time = milk_records.aggregate(Sum('second_time'))['second_time__sum']
    total_third_time = milk_records.aggregate(Sum('third_time'))['third_time__sum']
    total_milk = milk_records.aggregate(total_milk=Sum(F('first_time')+F('second_time')+F('third_time')))['total_milk']


   

    # Calculate total milk for each record as the sum of the three time fields
    milk_records = milk_records.annotate(computed_total_milk=F('first_time')+F('second_time')+F('third_time'))


    # Then aggregate over these calculated total_milk values for all records
    total_milk = milk_records.aggregate(total_milk_sum=Sum('computed_total_milk'))['total_milk_sum']
    logger.debug(f'Animal father: {animal.father}')
    active_tab = request.GET.get('active_tab', 'overview')
    print(time_filter)

    return render(request, 'dairy/animal_detail.html', {'animal': animal, 'milk_records': milk_records, 
                                                        'active_tab': active_tab,
                                                        'total_first_time': total_first_time,'total_second_time': total_second_time,'total_third_time': total_third_time,'total_milk': total_milk,'weights': weights, 'prev_weights': prev_weights, 'sort_by': sort_by, 'sort_order': sort_order,})


@login_required
def create_family(request, pk):
    animal = get_object_or_404(Animal, pk=pk)

    if request.method == 'POST':
        father_id = request.POST.get('father')
        mother_id = request.POST.get('mother')

        print(f"Father ID: {father_id}")
        print(f"Mother ID: {mother_id}")

        if father_id:
            father = get_object_or_404(Animal, pk=father_id)
            animal.father = father
        if mother_id:
            mother = get_object_or_404(Animal, pk=mother_id)
            animal.mother = mother

        try:
            animal.save()
            messages.success(request, "Family created successfully.")
            return redirect('dairy:animal_detail', pk=animal.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            # render the form again, possibly with error messages
    
    # Fetch all animals, excluding the current one
    animals = Animal.objects.exclude(pk=animal.pk)
    
    return render(request, 'dairy/create_family.html', {'animal': animal, 'animals': animals})


@login_required
def update_family(request, pk):
    animal = get_object_or_404(Animal, pk=pk)

    if request.method == 'POST':
        father_id = request.POST.get('father')
        mother_id = request.POST.get('mother')

        if father_id:
            father = get_object_or_404(Animal, pk=father_id)
            animal.father = father
        if mother_id:
            mother = get_object_or_404(Animal, pk=mother_id)
            animal.mother = mother

        animal.save()
        messages.success(request, "Family updated successfully.")
        return redirect('animal_detail', pk=animal.pk)

    return render(request, 'dairy/update_parents.html', {'animal': animal})

@login_required
def delete_family(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    relation_id = request.POST.get('relation_id')

    if request.method == 'POST':
        if relation_id == "father" and animal.father:
            animal.father.children_father.remove(animal)
            animal.father = None
        elif relation_id == "mother" and animal.mother:
            animal.mother.children_mother.remove(animal)
            animal.mother = None
        else:
            messages.error(request, "Invalid relation specified.")
            return redirect('dairy:animal_detail', pk=animal.pk)

        animal.save()
        messages.success(request, "Family relation deleted successfully.")
        return redirect('dairy:animal_detail', pk=animal.pk)

    return render(request, 'confirm_delete_family.html', {'animal': animal})



@login_required
def delete_animal(request, pk):
    if request.is_ajax() and request.method == "POST":
        animal = get_object_or_404(Animal, pk=pk, farm=request.user.farm)
        animal.delete()
        print(request.is_ajax())
        print(request.method)
        print(animal)

        return JsonResponse({"success": True})  # Sending an success response
    else:
        return JsonResponse({"success": False})  # Sending an error response


def milk_create_for_animal(request, animal_pk):
    animal = get_object_or_404(Animal, pk=animal_pk)

    if request.method == 'POST':
        form = MilkRecordForm(request.POST)
        if form.is_valid():
            milk_record = form.save(commit=False)
            milk_record.animal = animal
            milk_record.save()
            return redirect('dairy:milk-list')
    else:
        form = MilkRecordForm()

    return render(request, 'dairy/milk_records/create_update.html', {'form': form, 'edit_mode': False})

@login_required
def add_milk_record(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    if request.method == 'POST':
        form = MilkRecordForm(request.POST)
        if form.is_valid():
            milk_record = form.save(commit=False)  # Modify this line
            milk_record.animal = animal  # Add this line
            milk_record.save()  # Add this line
            return redirect('dairy/animal_detail.html', pk=animal_id)
    else:
        form = MilkRecordForm()
    return render(request, 'dairy/milk_records/add_milk_record.html', {'form': form, 'animal_id': animal_id, 'animal':animal})

@login_required
def get_milk_record(request, animal_id, date):
    animal = get_object_or_404(Animal, pk=animal_id)
    record = MilkRecord.objects.filter(animal=animal, date=date).first()
    
    if record:
        data = {
            'first_time': float(record.first_time),
            'second_time': float(record.second_time),
            'third_time': float(record.third_time)
        }
    else:
        data = {
            'first_time': '',
            'second_time': '',
            'third_time': ''
        }
    
    return JsonResponse(data)

@login_required
def edit_milk_record(request, milk_record_id):
    milk_record = get_object_or_404(MilkRecord, pk=milk_record_id)
    if request.method == 'POST':
        form = MilkRecordForm(request.POST, instance=milk_record)
        if form.is_valid():
            form.save(animal=milk_record.animal)  # Modify this line
            return redirect('dairy/animal_detail.html', pk=milk_record.animal.id)
    else:
        form = MilkRecordForm(instance=milk_record)
    return render(request, 'dairy/milk_records/edit_milk_record.html', {'form': form, 'milk_record':milk_record})

@login_required
def delete_milk_record(request, milk_record_id):
    milk_record = get_object_or_404(MilkRecord, pk=milk_record_id)
    animal_id = milk_record.animal.id
    milk_record.delete()
    return redirect('dairy/animal_detail.html', pk=animal_id)

from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator


from datetime import datetime, timedelta
from calendar import monthrange
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import models

def calculate_totals(milk_records):
    total_first_time = milk_records.aggregate(total=models.Sum('first_time'))['total'] or 0
    total_second_time = milk_records.aggregate(total=models.Sum('second_time'))['total'] or 0
    total_third_time = milk_records.aggregate(total=models.Sum('third_time'))['total'] or 0
    total_milk = total_first_time + total_second_time + total_third_time

    return total_first_time, total_second_time, total_third_time, total_milk
def get_date_range(time_filter):
    """
    Returns a tuple of start and end dates for a specific time filter.
    """
    if time_filter == 'last_7_days':
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    elif time_filter == 'last_day':
        end_date = timezone.now()
        start_date = end_date
    elif time_filter == 'today':
        end_date = timezone.now()
        start_date = end_date
    elif time_filter == 'yesterday':
        end_date = timezone.now() - timedelta(days=1)
        start_date = end_date
    elif time_filter == 'four_months':
        end_date = timezone.now()
        start_date = end_date - timedelta(days=120)
    elif time_filter == 'one_year':
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
    elif time_filter == 'this_month':
        end_date = timezone.now()
        start_date = end_date.replace(day=1)
    elif time_filter == 'last_month':
        end_date = timezone.now().replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif time_filter == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            raise ValueError('Invalid custom date range')
    else:
        raise ValueError('Invalid time filter')

    return start_date, end_date

@login_required
def animal_milk_list(request):
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')
    time_filter = request.GET.get('time_filter', 'today')  # Default to last 7 days

    sort_by_mapping = {
        'tag': 'animal__tag',
        'date': 'date',
        'first_time': 'first_time',
        'second_time': 'second_time',
        'third_time': 'third_time',
        'total_milk': '',
    }
    sort_by_field = sort_by_mapping.get(sort_by, 'date')

    farm = request.user.farm
    if sort_order == 'asc':
        milk_records = MilkRecord.objects.filter(animal__farm=farm).select_related('animal').order_by(sort_by_field)
    else:
        milk_records = MilkRecord.objects.filter(animal__farm=farm).select_related('animal').order_by(F(sort_by_field).desc(nulls_last=True))

    # Get the date range for the current and previous periods
    start_date, end_date = get_date_range(time_filter)

    if time_filter in ['today', 'yesterday']:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date

    elif time_filter in ['this_month', 'last_month']:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date.replace(day=1)
    else:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = start_date - (end_date - start_date + timedelta(days=1))

    # Apply the time filter to the querysets
    milk_records = milk_records.filter(date__range=[start_date, end_date])
    prev_milk_records = MilkRecord.objects.filter(animal__farm=farm, date__range=[prev_start_date, prev_end_date])

    # Calculate totals
    total_first_time, total_second_time, total_third_time, total_milk = calculate_totals(milk_records)
    prev_total_first_time, prev_total_second_time, prev_total_third_time, prev_total_milk = calculate_totals(prev_milk_records)

    if sort_by == 'total_milk':
        milk_records = sorted(milk_records, key=lambda x: x.total_milk, reverse=sort_order == 'desc')

    paginator = Paginator(milk_records, 50)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Create a dictionary to store milk records with the combination of animal's tag and date as the key
    milk_records_dict = {(record.animal.tag, record.date): record for record in milk_records}

    # Initialize the difference attributes for each milk_record
    for milk_record in page:
        milk_record.first_time_diff = 0
        milk_record.second_time_diff = 0
        milk_record.third_time_diff = 0
        milk_record.total_milk_diff = 0

        # Calculate differences based on the previous day's record
        previous_date = milk_record.date - timedelta(days=1)
        prev_record_key = (milk_record.animal.tag, previous_date)
        prev_record = milk_records_dict.get(prev_record_key)
        if prev_record:
            milk_record.first_time_diff = (milk_record.first_time or 0) - (prev_record.first_time or 0)
            milk_record.second_time_diff = (milk_record.second_time or 0) - (prev_record.second_time or 0)
            milk_record.third_time_diff = (milk_record.third_time or 0) - (prev_record.third_time or 0)
            milk_record.total_milk_diff = (milk_record.total_milk or 0) - (prev_record.total_milk or 0)

        # Print the results for debugging
        print(milk_record.first_time_diff, milk_record.second_time_diff, milk_record.third_time_diff, milk_record.total_milk_diff)

    return render(request, 'dairy/animal_milk_list.html', {
        'page': page,
        'milk_records': milk_records,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'time_filter': time_filter,
        'total_first_time': total_first_time,
        'total_second_time': total_second_time,
        'total_third_time': total_third_time,
        'total_milk': total_milk,
        'prev_total_first_time': prev_total_first_time,
        'prev_total_second_time': prev_total_second_time,
        'prev_total_third_time': prev_total_third_time,
        'prev_total_milk': prev_total_milk,
    })


@login_required
def total_milk_list(request):
    # Sorting, filtering and pagination logic remains similar
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')
    time_filter = request.GET.get('time_filter', 'today')  # Default to last 7 days

    farm = request.user.farm

    # Get the date range for the current and previous periods
    start_date, end_date = get_date_range(time_filter)

    if time_filter in ['today', 'yesterday']:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date
    elif time_filter in ['this_month', 'last_month']:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date.replace(day=1)
    else:
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = start_date - (end_date - start_date + timedelta(days=1))

    # Aggregate records by date
    aggregated_records = (
        MilkRecord.objects.filter(animal__farm=farm, date__range=[start_date, end_date])
        .values('date')
        .annotate(
            total_first_time=models.Sum('first_time'),
            total_second_time=models.Sum('second_time'),
            total_third_time=models.Sum('third_time'),
        )
        .annotate(
            total_milk=models.F('total_first_time') + models.F('total_second_time') + models.F('total_third_time')
        )
        .order_by(sort_by)
    )

    prev_aggregated_records = (
        MilkRecord.objects.filter(animal__farm=farm, date__range=[prev_start_date, prev_end_date])
        .values('date')
        .annotate(
            total_first_time=models.Sum('first_time'),
            total_second_time=models.Sum('second_time'),
            total_third_time=models.Sum('third_time'),
        )
        .annotate(
            total_milk=models.F('total_first_time') + models.F('total_second_time') + models.F('total_third_time')
        )
    )

    # Create a dictionary for easy lookup
    prev_totals_dict = {record['date']: record for record in prev_aggregated_records}
    # Get the date range for the current and previous periods
    milk_records = MilkRecord.objects.filter(animal__farm=farm)

    # Filter the milk_records based on the date range
    milk_records = milk_records.filter(date__range=[start_date, end_date])
    filtered_milk_records = milk_records.filter(date__range=[start_date, end_date])

    # Calculate totals
    total_first_time, total_second_time, total_third_time, total_milk = calculate_totals(filtered_milk_records)



    # Calculate the difference
   
    aggregated_list = list(aggregated_records)
    aggregated_list.sort(key=lambda x: x['date'])

    prev_record = None
    for record in aggregated_list:
        if prev_record:
            record['first_time_diff'] = (record['total_first_time'] or 0) - (prev_record['total_first_time'] or 0)
            record['second_time_diff'] = (record['total_second_time'] or 0) - (prev_record['total_second_time'] or 0)
            record['third_time_diff'] = (record['total_third_time'] or 0) - (prev_record['total_third_time'] or 0)
            record['total_diff'] = (record['total_milk'] or 0) - (prev_record['total_milk'] or 0)

           

        prev_record = record

    paginator = Paginator(aggregated_records, 50)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
   
    return render(request, 'dairy/total_milk_list.html', {
        'page': page,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'time_filter': time_filter,
        'total_first_time': total_first_time,
        'total_second_time': total_second_time,
        'total_third_time': total_third_time,
        'total_milk': total_milk,
    })


@login_required
def animal_milk_delete(request, pk):
    milk_record = get_object_or_404(MilkRecord, pk=pk)
    milk_record.delete()
    return redirect('dairy:animal_milk_list')

@login_required
def animal_milk_new(request):
    edit_mode = False
    milk_record = None
    farm = request.user.farm

    if request.method == "POST":
        form = MilkRecordForm(request.POST, farm=farm)
        if form.is_valid():
            animal = form.cleaned_data['animal']
            date = form.cleaned_data['date']
            milk_record, created = MilkRecord.objects.get_or_create(animal=animal, date=date)

            if not created:
                edit_mode = True

            form = MilkRecordForm(request.POST, instance=milk_record, farm=farm)
            if form.is_valid():
                form.save()
                return redirect('dairy:animal_milk_list')
    else:
        animal_id = request.GET.get('animal')
        date = request.GET.get('date')

        if animal_id and date:
            animal = get_object_or_404(Animal, pk=animal_id)
            milk_record, _ = MilkRecord.objects.get_or_create(animal=animal, date=date)
            edit_mode = True

        form = MilkRecordForm(instance=milk_record, farm=farm)

    return render(request, 'dairy/animal_milk_edit.html', {'form': form, 'edit_mode': edit_mode, 'milk_record': milk_record})

from datetime import timedelta

@login_required
def animal_weight_list(request):
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')

    # Map sort_by parameter to the correct field
    sort_by_mapping = {
        'tag': 'animal__tag',
        'date': 'date',
        'weight_kg': 'weight_kg',
        'weight_change_kg': '',  # This will be handled separately
        'weight_change_percent': '',  # This will be handled separately
    }
    sort_by_field = sort_by_mapping.get(sort_by, 'date')
    
    if sort_order == 'asc':
        weights = AnimalWeight.objects.filter(animal__farm=request.user.farm).select_related('animal').order_by(sort_by_field)
    else:
        weights = AnimalWeight.objects.filter(animal__farm=request.user.farm).select_related('animal').order_by(F(sort_by_field).desc(nulls_last=True))
    
    prev_weights = {}
    for weight in weights:
        prev_weight = AnimalWeight.objects.filter(animal=weight.animal, date__lt=weight.date).order_by('-date').first()
        prev_weights[weight.pk] = prev_weight

        # Calculate weight gain per day
        if prev_weight:
            days_passed = (weight.date - prev_weight.date).days
            weight_gain_per_day = (weight.weight_kg - prev_weight.weight_kg) / days_passed if days_passed != 0 else 0
            weight.weight_gain_per_day = round(weight_gain_per_day, 2)  # rounding to 2 decimal places

    return render(request, 'dairy/animal_weight_list.html', {'weights': weights, 'prev_weights': prev_weights, 'sort_by': sort_by, 'sort_order': sort_order})



@login_required
def animal_milk_edit(request, pk):
    milk_record = get_object_or_404(MilkRecord, pk=pk)
    edit_mode = True
    if request.method == "POST":
        form = MilkRecordForm(request.POST, instance=milk_record)
        if form.is_valid():
            milk_record = form.save(commit=False)
            milk_record.save()
            return redirect('dairy:animal_milk_list')
    else:
        form = MilkRecordForm(instance=milk_record, initial={'animal': milk_record.animal.pk})
    return render(request, 'dairy/animal_milk_edit.html', {'form': form, 'edit_mode': edit_mode, 'milk_record': milk_record})





@login_required
def animal_weight_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    weights = AnimalWeight.objects.filter(animal=animal)
    return render(request, 'dairy/animal_weight_detail.html', {'weights': weights, 'animal': animal})


@login_required
def animal_detail_weight_new(request, pk):  # Add the 'pk' argument here
    edit_mode = False
    animal = get_object_or_404(Animal, pk=pk)  # Get the Animal instance using the 'pk' argument
    

    if request.method == "POST":
        form = AnimalWeightForm(request.POST, user=request.user)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.animal = animal  # Set the animal attribute of the weight instance
            weight.save()
            return redirect('dairy:animal_weight_list')
    else:
        form = AnimalWeightForm(initial={'animal': animal}, user=request.user)  # Set the initial value of the 'animal' field

    return render(request, 'dairy/animal_weight_edit.html', {'form': form})

@login_required
def animal_weight_new(request):
    edit_mode = False
    if request.method == "POST":
        form = AnimalWeightForm(request.POST, user=request.user)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.save()
            return redirect('dairy:animal_weight_list')
    else:
        form = AnimalWeightForm(user=request.user)
    return render(request, 'dairy/animal_weight_edit.html', {'form': form})

@login_required
def animal_weight_edit(request, pk):
    weight = get_object_or_404(AnimalWeight, pk=pk)
    edit_mode = True
    if request.method == "POST":
        form = AnimalWeightForm(request.POST, instance=weight)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.save()
            return redirect('dairy:animal_weight_list')
    else:
        form = AnimalWeightForm(instance=weight, initial={'animal': weight.animal.pk})
    return render(request, 'dairy/animal_weight_edit.html', {'form': form, 'edit_mode': edit_mode, 'animal_weight_record': weight})


@login_required
def animal_weight_delete(request, pk):
    weight = get_object_or_404(AnimalWeight, pk=pk)
    weight.delete()
    return redirect('dairy:animal_weight_list')




@login_required
def customer_new(request, pk=None):
    edit_mode = False
    customer = None
    if pk:
        customer = get_object_or_404(Customer, pk=pk)
        edit_mode = True

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)  # Don't save to the database yet
            customer.farm = request.user.farm  # Associate customer with the logged-in user's farm
            customer.save()  # Now save to the database
            return redirect('dairy:customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'dairy/customer/customer_edit.html', {'form': form, 'edit_mode': edit_mode, 'customer': customer})

@login_required
def customer_list(request):
    customers = Customer.objects.filter(farm=request.user.farm).annotate(
        total_milk=Sum(
            Coalesce(F('milksale__first_sale'), Value(0)) + 
            Coalesce(F('milksale__second_sale'), Value(0)) + 
            Coalesce(F('milksale__third_sale'), Value(0)),
            output_field=DecimalField()
        ),
        total_amount=Sum('milksale__total_price')
    )
    return render(request, 'dairy/customer/customer_list.html', {'customers': customers})

from datetime import timedelta, datetime

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Default filtering is all milk sales
    milk_sales = MilkSale.objects.filter(customer=customer).order_by('-date')
    milk_payments = MilkPayment.objects.filter(customer=customer).order_by('-date')

    # Check if time_filter is provided in the request
    time_filter = request.GET.get('time_filter', 'this_month')
 
    if time_filter == "last_day":
        milk_sales = milk_sales.filter(date=datetime.now().date())
        milk_payments = milk_payments.filter(date=datetime.now().date())
    elif time_filter == "yesterday":
        milk_sales = milk_sales.filter(date=datetime.now().date() - timedelta(days=1))
        milk_payments = milk_payments.filter(date=datetime.now().date() - timedelta(days=1))
    elif time_filter == "last_7_days":
        milk_sales = milk_sales.filter(date__gte=datetime.now().date() - timedelta(days=7))
        milk_payments = milk_payments.filter(date__gte=datetime.now().date() - timedelta(days=7))
    elif time_filter == "this_month":
        month_start = datetime.now().replace(day=1).date()
        milk_sales = milk_sales.filter(date__gte=month_start)
        milk_payments = milk_payments.filter(date__gte=month_start)
    elif time_filter == "last_month":
        last_month_end = datetime.now().replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        milk_sales = milk_sales.filter(date__range=(last_month_start, last_month_end))
        milk_payments = milk_payments.filter(date__range=(last_month_start, last_month_end))
    elif time_filter == "four_months":
        four_months_start = datetime.now().date() - timedelta(days=120)
        milk_sales = milk_sales.filter(date__gte=four_months_start)
        milk_payments = milk_payments.filter(date__gte=four_months_start)
    elif time_filter == "one_year":
        one_year_start = datetime.now().date() - timedelta(days=365)
        milk_sales = milk_sales.filter(date__gte=one_year_start)
        milk_payments = milk_payments.filter(date__gte=one_year_start)
    totals = milk_sales.aggregate(
        total_first=Sum('first_sale') or 0,
        total_second=Sum('second_sale') or 0,
        total_third=Sum('third_sale') or 0,
        total_price=Sum('total_price')
    )
    totals['total_liters'] = (totals['total_first'] or 0) + (totals['total_second'] or 0) + (totals['total_third'] or 0)

    total_milk_sale = customer.total_sales_amount()
    total_paid = milk_payments.aggregate(total_paid=Sum('received_payment'))['total_paid'] or 0
    remaining_amount = total_milk_sale - total_paid


  

    return render(request, 'dairy/customer/customer_detail.html', {'customer': customer, 'milk_sales': milk_sales, 
                                                                   'milk_payments': milk_payments,
                                                                    'time_filter': time_filter,
                                                                      'totals': totals,
                                                                      'total_milk_sale': total_milk_sale,
    'total_paid': total_paid,
    'remaining_amount': remaining_amount
                                                                      })



@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('dairy:customer_list')  # 'dairy' should be replaced with your actual app's name

@login_required
def milk_sale_create(request):
    # Ensure the user has an associated farm
    if not hasattr(request.user, 'farm'):
        messages.error(request, 'User does not have an associated farm.')
        return redirect('your_redirect_location')  # Change 'your_redirect_location' to where you want to redirect in this case

    if request.method == "POST":
        form = MilkSaleForm(request.POST, user=request.user)  # Adjusting the form to consider the user's farm
        if form.is_valid():
            milk_sale = form.save(commit=False)
            milk_sale.farm = request.user.farm
            milk_sale.save()
            return redirect('dairy:milk_sale_list')
    else:
        form = MilkSaleForm(user=request.user)  # Adjusting the form to consider the user's farm
    context = {
        'form': form
    }
    return render(request, 'dairy/milk_records/milk_sale_form.html', context)


@login_required
def milk_sale_list(request):
    # Only fetch sales related to the logged-in user's farm
    sales = MilkSale.objects.filter(farm=request.user.farm)
    context = {
        'sales': sales
    }
    return render(request, 'dairy/milk_records/milk_sale_list.html', context)

@login_required
def milk_sale_edit(request, sale_id):
    milk_sale = get_object_or_404(MilkSale, id=sale_id)

    # Ensure the logged-in user has permission to edit this MilkSale (assuming by farm ownership)
    if milk_sale.farm != request.user.farm:
        return HttpResponseForbidden("You don't have permission to edit this MilkSale.")

    if request.method == "POST":
        form = MilkSaleForm(request.POST, instance=milk_sale, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dairy:milk_sale_list')
    else:
        form = MilkSaleForm(instance=milk_sale, user=request.user)

    context = {
        'form': form,
        'milk_sale': milk_sale
    }
    return render(request, 'dairy/milk_records/milk_sale_form.html', context)

@login_required
def milk_sale_delete(request, sale_id):
    milk_sale = get_object_or_404(MilkSale, id=sale_id)
    milk_sale.delete()
    return redirect('dairy:milk_sale_list')

@login_required
def add_milk_payment(request):
    
    # Ensure the user has an associated farm
    if not hasattr(request.user, 'farm'):
        messages.error(request, 'User does not have an associated farm.')
        return redirect('your_redirect_location')

    if request.method == "POST":
        form = MilkPaymentForm(request.POST, user=request.user)
        if form.is_valid():
            milk_payment = form.save(commit=False)
            milk_payment.farm = request.user.farm
            milk_payment.save()

            # Create or retrieve the 'Milk Sale' income category for the farm
            milk_sale_category, created = IncomeCategory.objects.get_or_create(farm=request.user.farm, name='Milk Sale')

            # As we're adding a new milk payment, there shouldn't be an associated income entry already. 
            # Hence, we create a new income instance directly.
            income = Income(user=request.user, farm=request.user.farm)
            income.date = milk_payment.date
            income.description = f'Milk payment from {milk_payment.customer.name}'
            income.amount = milk_payment.received_payment
            income.category = milk_sale_category
            income.milk_payment = milk_payment
            income.save()

            messages.success(request, 'Milk payment added successfully!')
            return redirect('dairy:customer_detail', pk=milk_payment.customer.pk)
    else:
        form = MilkPaymentForm(user=request.user)

    context = {
        'form': form
    }
    return render(request, 'dairy/customer/add_milk_payment.html', context)


@login_required
def update_milk_payment(request, milk_payment_id):
    farm = request.user.farm

    try:
        milk_payment = MilkPayment.objects.get(pk=milk_payment_id)
        edit_mode = True
    except MilkPayment.DoesNotExist:
        return HttpResponseNotFound("MilkPayment not found")

    if request.method == 'POST':
        form = MilkPaymentForm(request.POST, instance=milk_payment, user=request.user)
        if form.is_valid():
            milk_payment = form.save(commit=False)
            milk_payment.farm = request.user.farm
            milk_payment.save()

            # Code for auto-creating Income entry (same as in add_milk_payment view)
            milk_sale_category, created = IncomeCategory.objects.get_or_create(farm=request.user.farm, name='Milk Sale')
            try:
                income = Income.objects.get(milk_payment=milk_payment)
            except Income.DoesNotExist:
                income = Income(user=request.user, farm=request.user.farm)

            income.date = milk_payment.date
            income.description = f'Milk payment from {milk_payment.customer.name}'
            income.amount = milk_payment.received_payment
            income.category = milk_sale_category
            income.milk_payment = milk_payment
            income.save()

            messages.success(request, 'Milk Payment updated successfully!')
            return redirect('dairy:customer_detail', pk=milk_payment.customer.pk)
    else:
        form = MilkPaymentForm(instance=milk_payment, user=request.user)

    context = {
        'form': form,
        'edit_mode': edit_mode,
        'milk_payment': milk_payment
    }
    return render(request, 'dairy/customer/add_milk_payment.html', context)

@login_required
def delete_milk_payment(request, pk):
    milk_payment = MilkPayment.objects.get(pk=pk)
    milk_payment_pk = milk_payment.pk

    incomes = Income.objects.filter(milk_payment=milk_payment)
    
    if incomes.exists():
        for income in incomes:
            income_pk = income.pk
            print(f"Related income found for milk payment id {milk_payment_pk}: Income id {income_pk}")
            income.delete()
            print(f"Deleting related income with id {income_pk}")
    else:
        print(f"No related income found for milk payment id {milk_payment_pk}")

    milk_payment.delete()
    print(f"Deleting milk payment with id {milk_payment_pk}")

    return redirect('dairy:customer_detail', pk=milk_payment.customer.pk)

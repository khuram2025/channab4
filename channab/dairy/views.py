from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from .models import AnimalCategory, Animal, Breeding
from .forms import AnimalCategoryForm, AnimalForm, AnimalWeightForm, MilkRecordForm
from accounts.models import Farm
from .models import MilkRecord, Animal, AnimalWeight
from django.db.models import F
from datetime import timedelta, date
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.db.models import F, Q
from django.http import JsonResponse
from django.core import serializers

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
    three_months_ago = now - timedelta(days=90)  # approximately 3 months
    six_months_ago = now - timedelta(days=180)  # approximately 6 months
    one_year_ago = now - timedelta(days=365)  # 1 year
    one_and_half_years_ago = now - timedelta(days=547)  # 1.5 years

    selected_age_range = request.GET.get('age_range', 'all')

    if selected_age_range != 'all':
        # filter by age range as before
        if selected_age_range == '0-3M':
            animals = animals.filter(dob__gte=three_months_ago)
        elif selected_age_range == '3M-6M':
            animals = animals.filter(dob__gte=six_months_ago, dob__lt=three_months_ago)
        elif selected_age_range == '6M-1Y':
            animals = animals.filter(dob__gte=one_year_ago, dob__lt=six_months_ago)
        elif selected_age_range == '1Y-1.5Y':
            animals = animals.filter(dob__gte=one_and_half_years_ago, dob__lt=one_year_ago)
        else:  # '1.5Y+'
            animals = animals.filter(dob__lt=one_and_half_years_ago)


    # Add paginator and page object for 'all' animals
    paginator_all = Paginator(animals, 10)
    page_number_all = request.GET.get('page')
    page_objs_by_type['all'] = paginator_all.get_page(page_number_all)

    print('Total animals:', animals.count())
    print('Total pages:', paginator_all.num_pages)
    print('Has previous page:', page_objs_by_type['all'].has_previous())
    print('Has next page:', page_objs_by_type['all'].has_next())

    
    for animal_type in animal_types:
        animals_of_type = animals.filter(animal_type=animal_type)
        animals_by_type[animal_type] = animals_of_type
        counts_by_type[animal_type] = animals_of_type.count() 
        paginators_by_type[animal_type] = Paginator(animals_of_type, 14)
        page_number = request.GET.get('page')
        page_objs_by_type[animal_type] = paginators_by_type[animal_type].get_page(page_number)
    

    return render(request, 'dairy/animal_list.html', {
        'animals': animals, 
        'animals_by_type': animals_by_type, 
        'counts_by_type': counts_by_type, 
        'page_objs_by_type': page_objs_by_type,
        'selected_type': selected_type,
        'selected_age_range': selected_age_range,
    })


@login_required
def animal_create(request):
    farm = get_object_or_404(Farm, admin=request.user)
    edit_mode = False
    if request.method == 'POST':
        print("Form submitted")  # Add this line
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.farm = farm
            animal.save()
            return redirect('dairy:animal_list')
        else:
            print(form.errors)  # Add this line to print form errors
    else:
        form = AnimalForm()
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
    milk_records = milk_records.annotate(total_milk=F('first_time')+F('second_time')+F('third_time'))

    # Then aggregate over these calculated total_milk values for all records
    total_milk = milk_records.aggregate(total_milk_sum=Sum('total_milk'))['total_milk_sum']


    milk_records = MilkRecord.objects.filter(animal=animal)

   

    return render(request, 'dairy/animal_detail.html', {'animal': animal, 'milk_records': milk_records, 'total_first_time': total_first_time,'total_second_time': total_second_time,'total_third_time': total_third_time,'total_milk': total_milk,'weights': weights, 'prev_weights': prev_weights, 'sort_by': sort_by, 'sort_order': sort_order,})

@login_required
def update_parents(request, pk):
    farm = request.user.farm
    animal = get_object_or_404(Animal, pk=pk, farm=farm)

    if request.method == 'POST':
        father_id = request.POST.get('father')
        mother_id = request.POST.get('mother')

        if father_id:
            father = get_object_or_404(Animal, pk=father_id, farm=farm)
            if father != animal:
                animal.father = father

        if mother_id:
            mother = get_object_or_404(Animal, pk=mother_id, farm=farm)
            if mother != animal:
                animal.mother = mother

        animal.save()

        return redirect('animal_detail', pk=animal.pk)

    else: 
        animals = Animal.objects.filter(farm=farm).exclude(pk=animal.pk)
        return render(request, 'dairy/update_parents.html', {'animal': animal, 'animals': animals})

@login_required
def create_family(request, pk):
    farm = request.user.farm
    animal = get_object_or_404(Animal, pk=pk, farm=farm)

    if animal.father is not None and animal.mother is not None:
        messages.warning(request, "The animal already has a father and mother.")
        return redirect('animal_detail', pk=animal.pk)

    if request.method == 'POST':
        father_id = request.POST.get('father')
        mother_id = request.POST.get('mother')

        if father_id:
            father = get_object_or_404(Animal, pk=father_id, farm=farm)
            if father != animal:
                animal.father = father

        if mother_id:
            mother = get_object_or_404(Animal, pk=mother_id, farm=farm)
            if mother != animal:
                animal.mother = mother

        animal.save()

        return redirect('animal_detail', pk=animal.pk)

    else:
        animals = Animal.objects.filter(farm=farm).exclude(pk=animal.pk)
        return render(request, 'dairy/create_family.html', {'animal': animal, 'animals': animals})




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


def calculate_totals(milk_records):
    total_first_time = milk_records.aggregate(total=models.Sum('first_time'))['total'] or 0
    total_second_time = milk_records.aggregate(total=models.Sum('second_time'))['total'] or 0
    total_third_time = milk_records.aggregate(total=models.Sum('third_time'))['total'] or 0
    total_milk = total_first_time + total_second_time + total_third_time

    return total_first_time, total_second_time, total_third_time, total_milk

@login_required
def animal_milk_list(request):
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')
    time_filter = request.GET.get('time_filter', 'last_7_days')  # Default to last 7 days

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

    if time_filter == 'last_7_days':
        cutoff_date = timezone.now() - timedelta(days=7)
        milk_records = milk_records.filter(date__gte=cutoff_date)
    elif time_filter == 'last_day':
        cutoff_date = timezone.now() - timedelta(days=1)
        milk_records = milk_records.filter(date__gte=cutoff_date)
    elif time_filter == 'four_months':
        cutoff_date = timezone.now() - timedelta(days=120)
        milk_records = milk_records.filter(date__gte=cutoff_date)
    elif time_filter == 'one_year':
        cutoff_date = timezone.now() - timedelta(days=365)
        milk_records = milk_records.filter(date__gte=cutoff_date)
    elif time_filter == 'one_month':
        cutoff_date = timezone.now() - timedelta(days=30)
        milk_records = milk_records.filter(date__gte=cutoff_date)
    elif time_filter == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            cutoff_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            milk_records = milk_records.filter(date__range=[cutoff_date, end_date])
        else:
            messages.error(request, 'Invalid custom date range')
            return redirect('animal_milk_list')

    total_first_time, total_second_time, total_third_time, total_milk = calculate_totals(milk_records)

    if time_filter == 'last_7_days':
        cutoff_date = timezone.now() - timedelta(days=14)
        prev_cutoff_date = timezone.now() - timedelta(days=7)
    elif time_filter == 'last_day':
        cutoff_date = timezone.now() - timedelta(days=2)
        prev_cutoff_date = timezone.now() - timedelta(days=1)
    else:
        cutoff_date = timezone.now() - timedelta(days=30)
        prev_cutoff_date = timezone.now() - timedelta(days=60)
    # Add more conditions for other filters...

    previous_milk_records = MilkRecord.objects.filter(animal__farm=farm, date__range=[cutoff_date, prev_cutoff_date])
    prev_total_first_time, prev_total_second_time, prev_total_third_time, prev_total_milk = calculate_totals(previous_milk_records)

    if sort_by == 'total_milk':
        milk_records = sorted(milk_records, key=lambda x: x.total_milk, reverse=sort_order == 'desc')

    paginator = Paginator(milk_records, 50)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

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


from django.views import generic
from .models import Breeding
from .forms import BreedingForm
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def breeding_create(request):
    if request.method == 'POST':
        form = BreedingForm(request.POST)
        form.fields['bull'].queryset = Animal.objects.filter(sex='male')
        form.fields['animal'].queryset = Animal.objects.filter(sex='female')
        print("POST data: ", request.POST)
        if form.is_valid():
            print("Form is valid")
            breeding_record = form.save(commit=False)
            breeding_record.farm = request.user.farm
            print("Breeding record instance: ", breeding_record)
            breeding_record.save()
            return redirect('breeding_list')  # Replace with the actual url to the breeding list page
        else:
            print("Form is not valid")
            print("Form errors: ", form.errors)
    else:
        form = BreedingForm()
        form.fields['bull'].queryset = Animal.objects.filter(sex='male')
        form.fields['animal'].queryset = Animal.objects.filter(sex='female')
    return render(request, 'dairy/breeding_form.html', {'form': form})
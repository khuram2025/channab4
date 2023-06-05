from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import AnimalCategory, Animal
from .forms import AnimalCategoryForm, AnimalForm, AnimalWeightForm, MilkRecordForm
from accounts.models import Farm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import MilkRecord, Animal, AnimalWeight
from django.db.models import F
from datetime import timedelta, date
from django.db.models import Subquery, OuterRef


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
    animals = Animal.objects.filter(farm=farm)
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
    paginator_all = Paginator(animals, 200)
    page_number_all = request.GET.get('all_page')
    page_objs_by_type['all'] = paginator_all.get_page(page_number_all)
    
    for animal_type in animal_types:
        animals_of_type = animals.filter(animal_type=animal_type)
        animals_by_type[animal_type] = animals_of_type
        counts_by_type[animal_type] = animals_of_type.count() 
        paginators_by_type[animal_type] = Paginator(animals_of_type, 14)
        page_number = request.GET.get(f'{animal_type}_page')
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

    milk_records = MilkRecord.objects.filter(animal=animal)
   

    return render(request, 'dairy/animal_detail.html', {'animal': animal, 'milk_records': milk_records, 'weights': weights, 'prev_weights': prev_weights, 'sort_by': sort_by, 'sort_order': sort_order,})

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

@login_required
def animal_milk_list(request):
    sort_by = request.GET.get('sort_by', 'date')
    sort_order = request.GET.get('sort_order', 'desc')

    # Map sort_by parameter to the correct field
    sort_by_mapping = {
        'tag': 'animal__tag',
        'date': 'date',
        'first_time': 'first_time',
        'second_time': 'second_time',
        'third_time': 'third_time',
        'total_milk': '',  # This will be handled separately
    }
    sort_by_field = sort_by_mapping.get(sort_by, 'date')

    # Filter milk_records by the farm of the logged-in user
    farm = request.user.farm
    if sort_order == 'asc':
        milk_records = MilkRecord.objects.filter(animal__farm=farm).select_related('animal').order_by(sort_by_field)
    else:
        milk_records = MilkRecord.objects.filter(animal__farm=farm).select_related('animal').order_by(F(sort_by_field).desc(nulls_last=True))

    # Handle sorting by total_milk separately
    if sort_by == 'total_milk':
        milk_records = sorted(milk_records, key=lambda x: x.total_milk, reverse=sort_order == 'desc')

    return render(request, 'dairy/animal_milk_list.html', {'milk_records': milk_records, 'sort_by': sort_by, 'sort_order': sort_order})

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
    form = MilkRecordForm()

    if request.method == "POST":
        form = MilkRecordForm(request.POST)
        form.fields['animal'].queryset = Animal.objects.filter(farm=farm, sex='female')
        if form.is_valid():
            animal = form.cleaned_data['animal']
            date = form.cleaned_data['date']
            milk_record, created = MilkRecord.objects.get_or_create(animal=animal, date=date)

            if not created:
                edit_mode = True

            form = MilkRecordForm(request.POST, instance=milk_record)
            if form.is_valid():
                form.save()
                return redirect('dairy:animal_milk_list')
    else:
        animal_id = request.GET.get('animal')
        date = request.GET.get('date')
        form.fields['animal'].queryset = Animal.objects.filter(farm=farm, sex='female')

        if animal_id and date:
            animal = get_object_or_404(Animal, pk=animal_id)
            milk_record, _ = MilkRecord.objects.get_or_create(animal=animal, date=date)
            edit_mode = True

        form = MilkRecordForm(instance=milk_record)

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
        weights = AnimalWeight.objects.all().select_related('animal').order_by(sort_by_field)
    else:
        weights = AnimalWeight.objects.all().select_related('animal').order_by(F(sort_by_field).desc(nulls_last=True))
    
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
        form = AnimalWeightForm(request.POST)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.animal = animal  # Set the animal attribute of the weight instance
            weight.save()
            return redirect('dairy:animal_weight_list')
    else:
        form = AnimalWeightForm(initial={'animal': animal})  # Set the initial value of the 'animal' field

    return render(request, 'dairy/animal_weight_edit.html', {'form': form})

@login_required
def animal_weight_new(request):
    edit_mode = False
    if request.method == "POST":
        form = AnimalWeightForm(request.POST)
        if form.is_valid():
            weight = form.save(commit=False)
            weight.save()
            return redirect('dairy:animal_weight_list')
    else:
        form = AnimalWeightForm()
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

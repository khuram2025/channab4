from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import AnimalCategory, Animal
from .forms import AnimalCategoryForm, AnimalForm
from accounts.models import Farm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import MilkRecord, Animal
from .forms import MilkRecordForm

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


@login_required
def animal_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__admin=request.user)
    if request.method == 'POST':
        animal.delete()
        return HttpResponseRedirect(reverse('dairy:animal_list'))
    return render(request, 'dairy/delete.html', {'animal': animal})

@login_required
def animal_list(request):
    farm = request.user.farm
    animals = Animal.objects.filter(farm=farm)
    return render(request, 'dairy/animal_list.html', {'animals': animals})

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
    animal = get_object_or_404(Animal, pk=pk, farm__admin=request.user)
    milk_records = MilkRecord.objects.filter(animal=animal)
    return render(request, 'dairy/animal_detail.html', {'animal': animal, 'milk_records': milk_records})

@login_required
def animal_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk, farm__admin=request.user)
    if request.method == 'POST':
        animal.delete()
        return HttpResponseRedirect(reverse('dairy:animal_list'))
    return render(request, 'dairy/delete.html', {'animal': animal})


class MilkRecordListView(ListView):
    def get(self, request):
        milk_records = MilkRecord.objects.all()
        return render(request, 'dairy/milk_records/list.html', {'milk_records': milk_records})

class MilkRecordCreateUpdateView(CreateView):
    def get(self, request, pk=None):
        if pk:
            milk_record = get_object_or_404(MilkRecord, pk=pk)
            form = MilkRecordForm(instance=milk_record)
            edit_mode = True
        else:
            form = MilkRecordForm()
            edit_mode = False

        return render(request, 'dairy/milk_records/create_update.html', {'form': form, 'edit_mode': edit_mode})

    def post(self, request, pk=None):
        print("Post request received")
        if pk:
            milk_record = get_object_or_404(MilkRecord, pk=pk)
            form = MilkRecordForm(request.POST, instance=milk_record)
            edit_mode = True
        else:
            form = MilkRecordForm(request.POST)
            edit_mode = False

        print("Submitted Data:", request.POST)
        print("Form Animal Queryset:", form.fields['animal'].queryset)

        if form.is_valid():
            form.save()
            print("Form is valid and saved")
            return redirect('dairy:milk-list')
        else:
            print("Form Errors:", form.errors)
        return render(request, 'dairy/milk_records/create_update.html', {'form': form, 'edit_mode': edit_mode})

class MilkRecordUpdateView(UpdateView):
    def get(self, request, pk):
        milk_record = get_object_or_404(MilkRecord, pk=pk)
        form = MilkRecordForm(instance=milk_record)
        return render(request, 'dairy/milk_records/update.html', {'form': form})

    def post(self, request, pk):
        milk_record = get_object_or_404(MilkRecord, pk=pk)
        form = MilkRecordForm(request.POST, instance=milk_record)
        if form.is_valid():
            form.save()
            return redirect('dairy:milk-list')
        return render(request, 'dairy/milk_records/update.html', {'form': form})

class MilkRecordDeleteView(DeleteView):
    def get(self, request, pk):
        milk_record = get_object_or_404(MilkRecord, pk=pk)
        milk_record.delete()
        return redirect('dairy:milk-list')

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


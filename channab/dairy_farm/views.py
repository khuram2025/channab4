from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from datetime import date
from .models import AnimalCategory, Animal, MilkRecord, AnimalWeight
from .forms import AnimalCategoryForm, AnimalForm, MilkRecordForm, MemberForm, AnimalWeightForm
from django.db.models import Q

from django.db.models import F, FloatField, ExpressionWrapper, Window
from django.db.models.functions.window import Lag


class AnimalCategoryListView(ListView):
    model = AnimalCategory
    template_name = 'dairy_farm/backend/animalcategory_list.html'

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AnimalCategoryCreateView(AdminRequiredMixin, CreateView):
    model = AnimalCategory
    form_class = AnimalCategoryForm
    template_name = 'dairy_farm/backend/animalcategory_form.html'
    success_url = reverse_lazy('dairy_farm:animalcategory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context



class AnimalCategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = AnimalCategory
    form_class = AnimalCategoryForm
    template_name = 'dairy_farm/backend/animalcategory_form.html'
    success_url = reverse_lazy('dairy_farm:animalcategory_list')
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        return context


class AnimalCategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = AnimalCategory
    template_name = 'dairy_farm/backend/animalcategory_confirm_delete.html'
    success_url = reverse_lazy('dairy_farm:animalcategory_list')


@login_required
def category_list(request):
    if request.method == 'POST':
        new_category_title = request.POST.get('new_category')
        if new_category_title:
            AnimalCategory.objects.get_or_create(title=new_category_title)

    categories = AnimalCategory.objects.all()
    return render(request, 'dairy_farm/category_list.html', {'categories': categories})




@login_required
def animal_list(request):
    animals = Animal.objects.filter(user=request.user)
    context = {'animals': animals}
    return render(request, 'dairy_farm/animal_list.html', context)


from django.db.models import F, FloatField, ExpressionWrapper, Window
from django.db.models.functions import Lag

from django.db.models import F, FloatField, ExpressionWrapper, Window, OrderBy
from django.db.models.functions import Lag

class AnimalDetailView(LoginRequiredMixin, DetailView):
    model = Animal
    template_name = 'dairy_farm/animal_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MilkRecordForm()
        animal = self.get_object()
        context['animal_mother'] = AnimalRelation.objects.filter(animal=animal, relation_type="mother").first()
        context['animal_father'] = AnimalRelation.objects.filter(animal=animal, relation_type="father").first()
        context['animal_children'] = AnimalRelation.objects.filter(related_animal=animal)

        # Add the weight change calculation to the queryset
        animal_weights = animal.animalweight_set.annotate(
            weight_change=ExpressionWrapper(
                F('weight') - Window(Lag('weight', default=0), order_by=OrderBy(F('date'))),
                output_field=FloatField()
            )
        )
        context['animal_weights'] = animal_weights

        # Get the last weight and its difference
        last_weight = animal_weights.order_by('-date').first()
        if last_weight:
            context['last_weight'] = last_weight.weight
            context['last_weight_difference'] = last_weight.weight_change
        else:
            context['last_weight'] = 0
            context['last_weight_difference'] = 0

        return context


    def post(self, request, *args, **kwargs):
        form = MilkRecordForm(request.POST)
        animal = self.get_object()
        if form.is_valid():
            milk_record = form.save(commit=False)
            milk_record.animal = animal
            milk_record.save()
            return redirect('dairy_farm:animal_detail', pk=animal.id)
        else:
            context = self.get_context_data(object=animal, form=form)
            return self.render_to_response(context)


@login_required
def add_animal(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            new_animal = form.save(commit=False)
            new_animal.user = request.user
            new_animal.save()
            form.save_m2m()

            return redirect('dairy_farm:animal_list')
    else:
        form = AnimalForm()
    return render(request, 'dairy_farm/add_animal.html', {'form': form})


@login_required
def edit_animal(request, pk):
    animal = get_object_or_404(Animal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('dairy_farm:animal_list')
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'dairy_farm/edit_animal.html', {'form': form})

@login_required
def delete_animal(request, pk):
    animal = get_object_or_404(Animal, pk=pk, user=request.user)
    if request.method == 'POST':
        animal.delete()
        return redirect('dairy_farm:animal_list')
    return render(request, 'dairy_farm/delete_animal.html', {'animal': animal})

@login_required
def add_milk_record(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    if request.method == 'POST':
        form = MilkRecordForm(request.POST)
        if form.is_valid():
            milk_record = form.save(commit=False)  # Modify this line
            milk_record.animal = animal  # Add this line
            milk_record.save()  # Add this line
            return redirect('dairy_farm:animal_detail', pk=animal_id)
    else:
        form = MilkRecordForm()
    return render(request, 'dairy_farm/add_milk_record.html', {'form': form, 'animal_id': animal_id, 'animal': animal})


from django.http import JsonResponse

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
            return redirect('dairy_farm:animal_detail', pk=milk_record.animal.id)
    else:
        form = MilkRecordForm(instance=milk_record)
    return render(request, 'dairy_farm/edit_milk_record.html', {'form': form, 'milk_record': milk_record})



@login_required
def delete_milk_record(request, milk_record_id):
    milk_record = get_object_or_404(MilkRecord, pk=milk_record_id)
    animal_id = milk_record.animal.id
    milk_record.delete()
    return redirect('dairy_farm:animal_detail', pk=animal_id)


@login_required
def milk_records(request):
    milk_records = MilkRecord.objects.filter(animal__user=request.user).order_by('-date')
    context = {
        'milk_records': milk_records,
    }
    return render(request, 'dairy_farm/milk_records.html', context)




@login_required
def edit_all_milk_record(request, milk_record_id):
    milk_records = get_object_or_404(MilkRecord, pk=milk_record_id)
    animal = milk_records.animal

    if request.method == 'POST':
        form = MilkRecordForm(request.POST, instance=milk_records)
        if form.is_valid():
            form.save()
            return redirect('dairy_farm:milk_records')
    else:
        form = MilkRecordForm(instance=milk_records)

    context = {
        'form': form,
        'milk_records': milk_records,
        'animal': animal,
    }
    return render(request, 'dairy_farm/edit_milk_records.html', context)


@login_required
def delete_all_milk_record(request, milk_record_id):
    milk_record = get_object_or_404(MilkRecord, pk=milk_record_id)
    milk_record.delete()
    return redirect('dairy_farm:milk_records')

from django.forms.models import model_to_dict

@login_required
def add_milk_record_to_animal(request):
    if request.method == 'POST':
        form = MilkRecordForm(request.POST, user=request.user)
        print("Form data: ", request.POST)
        print("Animal field value: ", request.POST.get('animal'))
        print(f"Current user: {request.user}")
        print(f"Animals for user {request.user}: {Animal.objects.filter(user=request.user)}")


        if form.is_valid():
            milk_record = form.save(commit=False)
            milk_record.save()
            return redirect('dairy_farm:milk_records')
        else:
            print("Form errors:", form.errors)
    else:
        form = MilkRecordForm(user=request.user)
    return render(request, 'dairy_farm/add_milk_record_to_animal.html', {'form': form})



from .models import Farm, FarmMember, Member
from .forms import FarmForm

@login_required
def farm_list(request):
    user_member, created = Member.objects.get_or_create(id=request.user.id)
    farms = Farm.objects.filter(members=user_member)
    return render(request, 'dairy_farm/farm/farm_list.html', {'farms': farms})


@login_required
def add_farm(request):
    user_member, created = Member.objects.get_or_create(id=request.user.id)
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save()
            FarmMember.objects.create(user=user_member, farm=farm, role='Admin')
            return redirect('dairy_farm:farm_list')
    else:
        form = FarmForm()
    return render(request, 'dairy_farm/farm/farm_form.html', {'form': form})


@login_required
def edit_farm(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, members=request.user)
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            return redirect('dairy_farm:farm_list')
    else:
        form = FarmForm(instance=farm)
    return render(request, 'dairy_farm/farm_form.html', {'form': form})

from .forms import MemberCreationForm, FarmMemberForm
@login_required
def farm_detail(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id)
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            member = form.save()
            farm.members.add(member)
            farm.save()
            return redirect('farm_detail', farm_id=farm.id)
    else:
        form = MemberCreationForm()

    return render(request, 'dairy_farm/farm/farm_detail.html', {'farm': farm, 'form': form})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def add_member(request, farm_id):
    if request.method == 'POST':
        user_member, created = Member.objects.get_or_create(id=request.user.id)
        farm = get_object_or_404(Farm, id=farm_id, members=user_member)
        form = MemberForm(request.POST)
        if form.is_valid():
            new_member = form.save(commit=False)
            new_member.farm = farm
            new_member.save()
            return JsonResponse({'success': True, 'member': {
                'name': new_member.user.username,
                'role': new_member.role,
                'contact': new_member.user.mobile_number,
            }})
    return JsonResponse({'success': False})

    
@login_required
def add_member_page(request, farm_id):
    user_member, created = Member.objects.get_or_create(id=request.user.id)
    farm = get_object_or_404(Farm, id=farm_id, members=user_member)
    form = MemberForm()
    return render(request, 'dairy_farm/farm/add_member.html', {'form': form, 'farm_id': farm_id})



from .models import AnimalCategory, Animal, MilkRecord, AnimalRelation  # Add AnimalRelation to the imports
from .forms import AnimalCategoryForm, AnimalForm, MilkRecordForm, AnimalRelationForm  # Add AnimalRelationForm to the imports

# Create your views here.

# ... (existing views)

class AnimalRelationCreateView(LoginRequiredMixin, CreateView):
    model = AnimalRelation
    form_class = AnimalRelationForm
    template_name = 'dairy_farm/animalrelation_form.html'

    def get_success_url(self):
        return reverse_lazy('dairy_farm:animal_detail', kwargs={'pk': self.object.animal.id})

    def form_valid(self, form):
        form.instance.animal = Animal.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

class AnimalRelationUpdateView(LoginRequiredMixin, UpdateView):
    model = AnimalRelation
    form_class = AnimalRelationForm
    template_name = 'dairy_farm/animalrelation_form.html'

    def get_success_url(self):
        return reverse_lazy('dairy_farm:animal_detail', kwargs={'pk': self.object.animal.id})

class AnimalRelationDeleteView(LoginRequiredMixin, DeleteView):
    model = AnimalRelation
    template_name = 'dairy_farm/animalrelation_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('dairy_farm:animal_detail', kwargs={'pk': self.object.animal.id})


# Add AnimalWeight views

@login_required
def add_weight_record(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    if request.method == 'POST':
        form = AnimalWeightForm(request.POST)
        if form.is_valid():
            weight_record = form.save(commit=False)
            weight_record.animal = animal
            weight_record.save()
            return redirect('dairy_farm:animal_detail', pk=animal_id)
    else:
        form = AnimalWeightForm()
    return render(request, 'dairy_farm/weight/animal_weight_form.html', {'form': form, 'animal_id': animal_id, 'animal': animal})

@login_required
def edit_weight_record(request, weight_record_id):
    weight_record = get_object_or_404(AnimalWeight, pk=weight_record_id)
    if request.method == 'POST':
        form = AnimalWeightForm(request.POST, instance=weight_record)
        if form.is_valid():
            form.save()
            return redirect('dairy_farm:animal_detail', pk=weight_record.animal.id)
    else:
        form = AnimalWeightForm(instance=weight_record)
    return render(request, 'dairy_farm/weight/edit_weight_record.html', {'form': form, 'weight_record': weight_record})





@login_required
def animal_weight_delete_view(request, weight_record_id):
    weight_record = get_object_or_404(AnimalWeight, pk=weight_record_id)
    animal_id = weight_record.animal.id
    weight_record.delete()
    return redirect('dairy_farm:animal_detail', pk=animal_id)



from django import forms
from .models import AnimalCategory, Animal, Customer
from django.db.models import Q


class AnimalCategoryForm(forms.ModelForm):
    class Meta:
        model = AnimalCategory
        fields = ['title', 'image']


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['tag', 'image', 'dob', 'purchase_cost', 'status', 'sex', 'category', 'animal_type']

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super(AnimalForm, self).__init__(*args, **kwargs)
        if farm:
            # Get categories that belong to this farm or are site-level categories
            self.fields['category'].queryset = AnimalCategory.objects.filter(Q(farm=farm) | Q(is_site_level=True))



    
    


from .models import MilkRecord, Animal, AnimalWeight

class MilkRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.farm = kwargs.pop('farm', None)
        super(MilkRecordForm, self).__init__(*args, **kwargs)
        if self.farm:
            self.fields['animal'].queryset = Animal.objects.filter(farm=self.farm, sex='female', animal_type__in=['milking', 'preg_milking'])

    first_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    second_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    third_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = MilkRecord
        fields = ('animal', 'date', 'first_time', 'second_time', 'third_time')



class AnimalWeightForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AnimalWeightForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['animal'].queryset = Animal.objects.filter(farm__admin=self.user)

    class Meta:
        model = AnimalWeight
        fields = ['animal', 'weight_kg', 'date', 'description']


from django import forms
from .models import Breeding

from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'mobile_number', 'created_date']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'created_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

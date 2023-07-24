from django import forms
from .models import AnimalCategory, Animal
from django.db.models import Q


class AnimalCategoryForm(forms.ModelForm):
    class Meta:
        model = AnimalCategory
        fields = ['title', 'image']


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['tag', 'image', 'dob', 'purchase_cost', 'status', 'sex', 'category', 'animal_type']
    
    


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

class BreedingForm(forms.ModelForm):
    class Meta:
        model = Breeding
        fields = ['animal', 'breeding_date', 'method', 'bull', 'ai_dose_name', 'doctor_name', 'comments', 'lactation_number', 'attempt_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bull'].queryset = Animal.objects.filter(sex='male')
        self.fields['animal'].queryset = Animal.objects.filter(sex='female')
        self.fields['bull'].widget.attrs.update({'class': 'natural'})
        self.fields['ai_dose_name'].widget.attrs.update({'class': 'ai'})
        self.fields['doctor_name'].widget.attrs.update({'class': 'ai'})
    
    def save(self, commit=True):
        print("Saving form")
        instance = super().save(commit=False)
        if commit:
            instance.save()
            print("Form saved successfully")
        return instance

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('method')
        bull = cleaned_data.get('bull')
        ai_dose_name = cleaned_data.get('ai_dose_name')
        doctor_name = cleaned_data.get('doctor_name')

        if method == 'NATURAL' and not bull:
            self.add_error('bull', 'Bull is required for natural breeding')
        elif method == 'AI' and (not ai_dose_name or not doctor_name):
            self.add_error(None, 'AI Dose Name and Doctor Name are required for artificial insemination')

from django import forms
from .models import AnimalCategory, Animal

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
    animal = forms.ModelChoiceField(queryset=Animal.objects.none())  # Will be set in the view
    first_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    second_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    third_time = forms.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = MilkRecord
        fields = ('animal', 'date', 'first_time', 'second_time', 'third_time')



class AnimalWeightForm(forms.ModelForm):
    class Meta:
        model = AnimalWeight
        fields = ['animal', 'weight_kg', 'date', 'description']
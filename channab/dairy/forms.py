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


from .models import MilkRecord, Animal

class MilkRecordForm(forms.ModelForm):
    class Meta:
        model = MilkRecord
        fields = ('date', 'first_time', 'second_time', 'third_time')

    def _init_(self, *args, **kwargs):
        self.animal = kwargs.pop('animal', None)
        super(MilkRecordForm, self)._init_(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        milk_record = super(MilkRecordForm, self).save(commit=False)
        milk_record.animal = kwargs.get('animal')  # Add this line
        if commit:
            milk_record.save()
        return milk_record
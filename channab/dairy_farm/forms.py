from django import forms
from .models import Animal, AnimalCategory, MilkRecord

class AnimalCategoryForm(forms.ModelForm):
    class Meta:
        model = AnimalCategory
        fields = ['title', 'category_image',]




class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'tag',
            'image',
            'dob',
            'purchase_cost',
            'status',
            'sex',
            'category',
        ]

        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }

from django.core.exceptions import ValidationError

class AnimalChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AnimalChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return f"{obj.tag} ({obj.category})"

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            return Animal.objects.get(user=self.user, tag=value)
        except Animal.DoesNotExist:
            raise ValidationError(f"Animal instance with tag {value} does not exist.")







class MilkRecordForm(forms.ModelForm):
    class Meta:
        model = MilkRecord
        fields = ('date', 'first_time', 'second_time', 'third_time')

    def __init__(self, *args, **kwargs):
        self.animal = kwargs.pop('animal', None)
        super(MilkRecordForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        milk_record = super(MilkRecordForm, self).save(commit=False)
        milk_record.animal = kwargs.get('animal')  # Add this line
        if commit:
            milk_record.save()
        return milk_record






from .models import AnimalCategory, Animal, MilkRecord, Member, Farm, FarmMember
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Member, FarmMember

class MemberCreationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ('username', 'image', 'job_title', 'mobile_number', 'first_name', 'last_name', 'email')

class FarmMemberForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=Member.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    role = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = FarmMember
        fields = ('user', 'role')

class MemberForm(forms.ModelForm):
    class Meta:
        model = FarmMember
        fields = ['user', 'role']

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = Member.objects.all().exclude(is_superuser=True)


from django import forms
from .models import AnimalCategory, Animal, MilkRecord, Member, Farm, FarmMember

# ...

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'description', 'location']

    def __init__(self, *args, **kwargs):
        super(FarmForm, self).__init__(*args, **kwargs)



from .models import AnimalCategory, Animal, MilkRecord, AnimalRelation  # Add AnimalRelation to the imports

# ... (existing forms)

class AnimalRelationForm(forms.ModelForm):
    class Meta:
        model = AnimalRelation
        fields = ['related_animal', 'relation_type']

from .models import AnimalWeight

class AnimalWeightForm(forms.ModelForm):
    class Meta:
        model = AnimalWeight
        fields = ['date', 'weight']

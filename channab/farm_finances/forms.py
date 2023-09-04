from django import forms
from .models import IncomeCategory, ExpenseCategory
from django.forms import DateInput

class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ('name',)

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ('name',)

from django import forms
from .models import Income, Expense

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('date', 'description', 'amount', 'category', 'image')
        widgets = {
            'date': DateInput(attrs={'class': 'form-control date-input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super(IncomeForm, self).__init__(*args, **kwargs)
        if farm:
            self.fields['category'].queryset = IncomeCategory.objects.filter(farm=farm)

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'description', 'amount', 'category', 'image']
        widgets = {
            'date': DateInput(attrs={'class': 'form-control date-input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if farm:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(farm=farm)

from rest_framework import serializers
from dairy.models import Animal
from farm_finances.models import Income, Expense, IncomeCategory, ExpenseCategory

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'age', 'sex']  # add more fields here if needed

class CategorySummarySerializer(serializers.Serializer):
    category = serializers.CharField()
    total_amount = serializers.FloatField()
    
from rest_framework import serializers
from .models import Animal, AnimalWeight, MilkRecord

class AnimalWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalWeight
        fields = ['weight_kg', 'date', 'description']

class MilkRecordSerializer(serializers.ModelSerializer):
    total_milk = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = MilkRecord
        fields = ['date', 'first_time', 'second_time', 'third_time', 'total_milk']

class AnimalSerializer(serializers.ModelSerializer):
    weights = AnimalWeightSerializer(many=True, read_only=True)
    milk_records = MilkRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Animal
        fields = ['id', 'tag', 'dob', 'image', 'status', 'sex', 'category', 'animal_type', 'weights', 'milk_records']

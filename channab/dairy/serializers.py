from rest_framework import serializers
from .models import Animal, AnimalWeight, MilkRecord

class AnimalWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalWeight
        fields = ['weight_kg', 'date', 'description']

class MilkRecordSerializer(serializers.ModelSerializer):
    animal = serializers.PrimaryKeyRelatedField(queryset=Animal.objects.all())
    total_milk = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = MilkRecord
        fields = ['animal', 'date', 'first_time', 'second_time', 'third_time', 'total_milk']

    def create(self, validated_data):
        animal = validated_data.get('animal')
        date = validated_data.get('date')
        milk_record, created = MilkRecord.objects.get_or_create(animal=animal, date=date, defaults=validated_data)
        if not created:
            # Update the existing record if it already exists
            for attr, value in validated_data.items():
                setattr(milk_record, attr, value)
            milk_record.save()
        return milk_record

class MilkAnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'tag', 'sex', 'animal_type']

class AnimalSerializer(serializers.ModelSerializer):
    weights = AnimalWeightSerializer(many=True, read_only=True)
    milk_records = MilkRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Animal
        fields = ['id', 'tag', 'dob', 'image', 'status', 'sex', 'category', 'animal_type', 'weights', 'milk_records']


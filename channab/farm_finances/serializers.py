
from .models import Income
from rest_framework import serializers, viewsets

class IncomeSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Income
        fields = ['user', 'farm', 'date', 'description', 'amount', 'category', 'image']



 

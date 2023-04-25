from django.contrib import admin

from .models import AnimalCategory, Animal, Farm, AnimalRelation, AnimalWeight

admin.site.register(AnimalCategory)
admin.site.register(Animal)
admin.site.register(Farm)
admin.site.register(AnimalRelation)
admin.site.register(AnimalWeight)



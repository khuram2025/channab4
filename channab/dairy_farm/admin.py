from django.contrib import admin

from .models import AnimalCategory, Animal, Farm, AnimalRelation

admin.site.register(AnimalCategory)
admin.site.register(Animal)
admin.site.register(Farm)
admin.site.register(AnimalRelation)



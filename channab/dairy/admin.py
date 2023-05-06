
from django.contrib import admin
from .models import Animal, AnimalCategory, MilkRecord

class AnimalAdmin(admin.ModelAdmin):
    pass

class AnimalCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Animal, AnimalAdmin)
admin.site.register(MilkRecord)
admin.site.register(AnimalCategory, AnimalCategoryAdmin)

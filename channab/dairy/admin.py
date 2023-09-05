
from django.contrib import admin
from .models import Animal, AnimalCategory, Customer, MilkRecord, MilkSale

class AnimalAdmin(admin.ModelAdmin):
    list_display = ('tag', 'farm', 'get_farm_admin')
    list_filter = ('farm', 'farm__admin')
    
    def get_farm_admin(self, obj):
        return obj.farm.admin
    get_farm_admin.short_description = 'Farm Admin'


class AnimalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'farm')

admin.site.register(Animal, AnimalAdmin)
admin.site.register(MilkRecord)
admin.site.register(Customer)
admin.site.register(MilkSale)

admin.site.register(AnimalCategory, AnimalCategoryAdmin)

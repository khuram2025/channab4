from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Farm, SalaryComponent, SalaryTransaction
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('mobile', 'email', 'first_name', 'last_name', 'role', 'farm', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'role','last_login')
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Farm', {'fields': ('farm',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'email', 'first_name', 'last_name', 'role', 'farm'),
        }),
    )
    search_fields = ('mobile', 'email', 'first_name', 'last_name')
    ordering = ('mobile',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Farm)

class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'duration', 'member')
    search_fields = ('name', 'member__first_name', 'member__last_name')
    ordering = ('member', 'name')

admin.site.register(SalaryComponent, SalaryComponentAdmin)

class SalaryTransactionAdmin(admin.ModelAdmin):
    list_display = ('farm_member', 'component', 'amount_paid', 'transaction_date')
    search_fields = ('farm_member__first_name', 'farm_member__last_name', 'component__name')
    ordering = ('transaction_date', 'farm_member')

admin.site.register(SalaryTransaction, SalaryTransactionAdmin)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'email', 'facebook', 'youtube')
    search_fields = ('user__mobile', 'email', 'first_name', 'last_name')
    ordering = ('user',)

admin.site.register(Profile, ProfileAdmin)

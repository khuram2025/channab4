from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Farm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('mobile', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active', 'role',)
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'email', 'first_name', 'last_name', 'role'),
        }),
    )
    search_fields = ('mobile', 'email', 'first_name', 'last_name')
    ordering = ('mobile',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Farm)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'email', 'facebook', 'youtube')
    search_fields = ('user__mobile', 'email', 'first_name', 'last_name')
    ordering = ('user',)

admin.site.register(Profile, ProfileAdmin)

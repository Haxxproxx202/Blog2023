from django.contrib import admin
from .models import CustomUserModel


@admin.register(CustomUserModel)
class CustomUser(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'type')
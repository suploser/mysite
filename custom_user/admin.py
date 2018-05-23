from django.contrib import admin
from .models import User, ConfirmString
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'email','has_confirmed', 'is_supuser')

@admin.register(ConfirmString)
class ConfirmStringAdmin(admin.ModelAdmin):
    list_display = ('user', 'reg_time', 'token')
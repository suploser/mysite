from django.contrib import admin
from .models import FavorCount, FavorRecord
# Register your models here.

@admin.register(FavorCount)
class ReadNumsAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'favor_num')

@admin.register(FavorRecord)
class ReadNumsAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'user', 'favor_time')

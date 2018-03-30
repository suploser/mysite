from django.contrib import admin
from .models import ReadNums
# Register your models here.

@admin.register(ReadNums)
class ReadNumsAdmin(admin.ModelAdmin):
    list_display = ('read_num', 'read_date','content_type', 'object_id',\
     'content_object')

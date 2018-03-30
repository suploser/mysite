from django.contrib import admin
from .models import BlogType, Blog

@admin.register(BlogType)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name',)

@admin.register(Blog)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog_type', 'get_read_num', 'author',\
        'created_time', 'last_update_time',)
    '''
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num', 'blog')
    '''
# admin.models.register(Blog, BlogTypeAdmin)
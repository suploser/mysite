from django.contrib import admin
from .models import BlogType, Blog, User

@admin.register(BlogType)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name',)

@admin.register(Blog)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'blog_type', 'get_read_num', 'author',\
        'created_time', 'last_update_time',)
    '''
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num', 'blog')
    '''
# admin.models.register(Blog, BlogTypeAdmin)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')
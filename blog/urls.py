from django.contrib import admin
from django.urls import path
from .views import blog_detail, blogs_by_type, blogs_list, blogs_by_date, blog_add,\
edit, ajax_get_content, edit_ajax_add, blog_search

urlpatterns = [
    path('', blogs_list, name='blogs_list'),
    path('add/', blog_add, name='blog_add'),
    path('search/', blog_search, name='search'),
    path('<int:blog_id>/', blog_detail, name='blog_detail'),
    path('type/<int:blog_type_id>', blogs_by_type, name='blogs_by_type'),
    path('date/<int:year>/<int:month>', blogs_by_date, name='blogs_by_date'),
    path('edit/<int:blog_id>', edit, name="edit"),
    path('ajax_get_content/<int:blog_id>', ajax_get_content, name='ajax_get_content'),
    path('edit_ajax_add/<int:blog_id>', edit_ajax_add, name="edit_ajax_add"),
]
from django import template
from blog.models import BlogType


register = template.Library()

@register.simple_tag
def get_blog_type():
    return BlogType.objects.all()

# 自定义过滤器
@register.filter
def cut(value, arg):
    return value.replace('','')
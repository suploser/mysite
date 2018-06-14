from django import template
from blog.models import BlogType,Blog


register = template.Library()

@register.simple_tag
def get_blog_type():
    return BlogType.objects.all()

@register.simple_tag
def get_blog_nums():
    return Blog.objects.all().count()

@register.simple_tag
def get_create_time():
    from datetime import datetime
    c_time = datetime(2018,1,1,0,0).timestamp()
    now = datetime.now().timestamp()
    time_diff = now - c_time
    day_diff = int(time_diff/60/60/24)
    return day_diff

# 自定义过滤器
@register.filter
def cut(value, arg):
    return value.replace('','')


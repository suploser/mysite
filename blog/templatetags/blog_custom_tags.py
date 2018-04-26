from django import template
from blog.models import BlogType

register = template.Library()
@register.simple_tag
def get_blog_type():
    return BlogType.objects.all()

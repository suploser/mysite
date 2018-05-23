from django import template
from django.contrib.contenttypes.models import ContentType
from favor.models import FavorCount, FavorRecord
from custom_user.models import User

register = template.Library()
@register.simple_tag
def get_favor_num(obj):
    content_type = ContentType.objects.get_for_model(model=obj)
    favorCount, created = FavorCount.objects.get_or_create(content_type=content_type, 
        object_id=obj.id)
    return favorCount.favor_num

@register.simple_tag
def get_favor_status(obj, request):
    content_type = ContentType.objects.get_for_model(model=obj)
    if not request.session.get('username'):
        return ''
    user = User.objects.get(username=request.session.get('username'))
    if FavorRecord.objects.filter(content_type=content_type, object_id=obj.id, 
        user=user).exists():
        return 'active'
    else:
        return ''


from django import template
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
# 自定义标签
register = template.Library()
@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(model=obj)
    comment_count = Comment.objects.filter(content_type=content_type, 
        object_id=obj.id).count()
    return comment_count

@register.simple_tag
def get_comments(obj):
    content_type = ContentType.objects.get_for_model(model=obj)
    comments = Comment.objects.filter(content_type=content_type, 
        object_id=obj.id, root=None).order_by('-create_time')
    return comments

@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(model=obj)
    from comment.forms import CommentForm
    comment_form = CommentForm(initial={'content_type':content_type.model, 'object_id':obj.id,
         'reply_comment_id':0})
    return comment_form
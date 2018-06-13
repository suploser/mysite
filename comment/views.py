from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .models import Comment
from comment.forms import CommentForm
# Create your views here.
# 写一个装饰器来验证是否登录
def update_comment(request):
    data={}
    comment_form = CommentForm(request.POST, session=request.session)
    if comment_form.is_valid():
        user = comment_form.cleaned_data['user']
        content_object = comment_form.cleaned_data['content_object']
        comment_content = comment_form.cleaned_data['comment_content']
        comment = Comment(user=user, content_object=content_object, content=
            comment_content)
        parent = comment_form.cleaned_data['parent']
        if parent:
            comment.root = parent.root if parent.root else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['avatar_url'] = comment.user.get_avatar_url()
        data['reply_to'] = comment.reply_to.username if parent else ''
        data['reply_avatar_url'] = comment.reply_to.get_avatar_url() if parent else ''
        data['id'] = comment.id
        data['root_id'] = comment.root.id if parent else ''
        from datetime import datetime
        #时区转换
        data['comment_time'] = datetime.fromtimestamp(comment.create_time.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
        data['comment_content'] = comment.content

    else:
        data['status'] = 'ERROR'
        # form.errors包括non_field_errors
        data['message'] = list(comment_form.errors.values())[0]

    return JsonResponse(data)
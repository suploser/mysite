from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Comment
from comment.forms import CommentForm
from utils import SendEmail
# Create your views here.
# 写一个装饰器来验证是否登录
def update_comment(request):
    data={}
    send_email = SendEmail()
    # 填充数据
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
        email_data = {
            'comment_url':'{0}/blog/{1}#{2}'.format(settings.SITE_IP, content_object.id, comment.id),
            'comment_username':comment.user.username,
            'comment_content':comment.content
        }
        if not data['root_id']:
            subject = '新的博客评论'
            module = 'email/comment_email.html'
            send_email.send_email_by_template(subject, module, email_data, settings.EMAIL_DEFAULT_FROM)
        else:
            subject='新回复'
            module = 'email/reply_email.html'
            email_to = comment.reply_to.email
            send_email.send_email_by_template(subject, module, email_data, email_to)
    else:
        data['status'] = 'ERROR'
        # form.errors包括non_field_errors
        data['message'] = list(comment_form.errors.values())[0]

    return JsonResponse(data)
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .models import Comment
from comment.forms import CommentForm
# Create your views here.
def update_comment(request):
    data={}
    comment_form = CommentForm(request.POST, session=request.session)
    if comment_form.is_valid():
        user = comment_form.cleaned_data['user']
        content_object = comment_form.cleaned_data['content_object']
        comment_content = comment_form.cleaned_data['comment_content']
        comment = Comment(user=user, content_object=content_object, content=
            comment_content)
        comment.save()
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['comment_time'] = comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        data['comment_content'] = comment.content

    else:
        data['status'] = 'ERROR'
        # form.errors包括non_field_errors
        data['message'] = list(comment_form.errors.values())[0]

    return JsonResponse(data)
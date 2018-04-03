from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Comment
# Create your views here.
def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))

    user = request.session.get('user')
    username = request.session.get('username')
    password = request.session.get('password')
    User = ContentType.objects.filter(model=user)[1].model_class()
    user = User.objects.filter(username=username, password=password).first()
    
    content = request.POST.get('content','')
    if not content:
        return render(request, 'error.html',{'message':'内容为空',
            'redirect_to':referer})
    try:
        object_id = int(request.POST.get('object_id'))
        content_type = request.POST.get('content_type')
        model_class = ContentType.objects.get(model=content_type).model_class()
        content_object = model_class.objects.get(id=object_id)
    except:
        return render(request, 'error.html',{'message':'评论类型错误',
            'redirect_to':referer})
    

    comment = Comment(user=user, content_object=content_object,
        content=content)
    comment.save()
    return redirect(referer)

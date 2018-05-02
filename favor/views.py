from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import FavorCount, FavorRecord
from custom_user.models import User
# Create your views here.
def Response(status, message):
    data = {}
    data['status'] = status
    data['message'] = message
    return JsonResponse(data)

def favor_count(request):
    if request.session.get('username'):
        user = User.objects.filter(username=request.session.get('username')).first()
    else:
        return Response('Fail', '您未登录, 不可点赞')
    content_type = request.GET.get('content_type')
    content_type = ContentType.objects.get(model=content_type)
    object_id = int(request.GET.get('object_id'))
    is_active = request.GET.get('is_active')
    if is_active == 'false':
        # 未点赞，进行点赞
        if not FavorRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            FavorRecord.objects.create(content_type=content_type, 
                object_id=object_id, user=user)
            favorCount, created = FavorCount.objects.get_or_create(content_type=content_type, 
                object_id=object_id)

            favorCount.favor_num += 1
            favorCount.save()
            return Response('Success', favorCount.favor_num)
        else:
            # 已点赞
            return Response('Fail', '您已点赞过，不可重复点赞')

    else:
        # 已点赞,取消点赞,后台仍需验证
        if FavorRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            favorRecord = FavorRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            favorRecord.delete()
            favorCount, created = FavorCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            favorCount.favor_num -= 1
            favorCount.save()
            return Response('Success', favorCount.favor_num)
        else:
            # 未点赞
            return Response('Fail', '您还未点赞，不可取消点赞')
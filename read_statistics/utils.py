from django.contrib.contenttypes.models import ContentType
from .models import ReadNums

def read_statistics_once_read(request, model_obj):
    content_type = ContentType.objects.get_for_model(model_obj)
    cookies_key = '%s_%s_read' % (content_type.model, model_obj.id)
    if not request.COOKIES.get(cookies_key):
        global read_num_obj
        try:
            read_num_obj = ReadNums.objects.get(content_type=content_type, \
                object_id=model_obj.id)
        except:
            read_num_obj = ReadNums(content_type=content_type,\
                object_id=model_obj.id)
        finally:
            read_num_obj.read_num += 1
            read_num_obj.save()
    return cookies_key
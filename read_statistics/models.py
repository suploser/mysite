from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class ReadNums(models.Model):
    
    read_num = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class ReadNumExpand(object):

    def get_read_num(self):
        try:
            content_type = ContentType.objects.get_for_model(self)
            read_num_obj = ReadNums.objects.get(content_type=content_type, \
                object_id=self.id)
            return read_num_obj.read_num
        except:
            return 0

    def read_statistics_once_read(self, request):
        content_type = ContentType.objects.get_for_model(self)
        cookies_key = '%s_%s_read' % (content_type.model, self.id)
        if not request.COOKIES.get(cookies_key):
            global read_num_obj
            try:
                read_num_obj = ReadNums.objects.get(content_type=content_type, \
                    object_id=self.id)
            except:
                read_num_obj = ReadNums(content_type=content_type,\
                    object_id=self.id)
            finally:
                read_num_obj.read_num += 1
                read_num_obj.save()
        return cookies_key

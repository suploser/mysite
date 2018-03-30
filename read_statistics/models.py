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

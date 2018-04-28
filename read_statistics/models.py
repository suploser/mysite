from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class ReadNums(models.Model):
    read_num = models.IntegerField(default=0)
    # 当删除博客时不会删除阅读量记录,因为外键是contenttype
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)    
    object_id = models.PositiveIntegerField()
    read_date = models.DateField(default=timezone.now)
    content_object = GenericForeignKey('content_type', 'object_id')

# class ReadDeail(models.Model):


        
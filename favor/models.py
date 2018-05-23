from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from custom_user.models import User
# Create your models here.
class FavorCount(models.Model):
    content_type = models.ForeignKey(ContentType, 
        on_delete=models.CASCADE)    
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 
        'object_id')
    favor_num = models.IntegerField(default=0)

class FavorRecord(models.Model):
    content_type = models.ForeignKey(ContentType, 
        on_delete=models.CASCADE)    
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 
        'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favor_time = models.DateTimeField(auto_now_add=True)

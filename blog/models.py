from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.fields import GenericRelation
# from django.contrib.auth.models import User
from custom_user.models import User
from read_statistics.models import ReadNums
from read_statistics.utils import ReadNumExpand
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def blog_count(self):
        return self.blog_set.count()#指向该表对象的从表集合

    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadNumExpand):
    title = models.CharField(max_length=50)
    blog_type = models.ManyToManyField(BlogType)    
    # read_nums = models.IntegerField(default=0)
    content = RichTextUploadingField()
    # content = models.TextField()
    read_num_obj = GenericRelation(ReadNums)
    author = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_time = models.DateTimeField(auto_now_add=True)
    # 修改后自动更新
    last_update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']
'''
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)'''


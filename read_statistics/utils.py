# 阅读统计
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from .models import ReadNums


class ReadNumExpand(object):

    def get_read_num(self):
        return self.get_total_read_nums()

    def read_statistics_once_read(self, request):
        content_type = ContentType.objects.get_for_model(self)
        cookies_key = '%s_%s_read' % (content_type.model, self.id)
        read_date = timezone.now().date()
        if not request.COOKIES.get(cookies_key):
            global read_num_obj
            try:
                read_num_obj = ReadNums.objects.get(content_type=content_type, \
                    object_id=self.id, read_date=read_date)
            except:
                read_num_obj = ReadNums(content_type=content_type,\
                    object_id=self.id, read_date=read_date)
            finally:
                read_num_obj.read_num += 1
                read_num_obj.save()
        return cookies_key

    def get_total_read_nums(self):
        content_type = ContentType.objects.get_for_model(self)
        read_num_set = ReadNums.objects.filter(content_type=content_type, \
            object_id=self.id)
        if read_num_set:
            total_read_nums = read_num_set.aggregate(read_num=Sum('read_num'))
            return total_read_nums['read_num']
        else:
            return 0

    @classmethod
    def get_seven_days_read_nums(cls):
        content_type = ContentType.objects.get_for_model(cls)
        read_date = timezone.now().date()
        date_list = []
        read_num_list = []
        for i in range(7,0,-1):
            date = read_date - timedelta(days=i)
            date_list.append(date.strftime('%m-%d'))
            global total_nums_by_date
            read_num_set = ReadNums.objects.filter(
                content_type=content_type, read_date=date)
            if read_num_set:
                total_nums_by_date = read_num_set.aggregate(read_nums_by_day=\
                    Sum('read_num'))
                read_num_list.append(total_nums_by_date['read_nums_by_day'])
            else:
                read_num_list.append(0)
            
        return read_num_list, date_list

    @classmethod
    def get_one_day_hot_blog_list(cls, date):
        one_day_hot_blog_list = cls.objects.filter(
            read_num_obj__read_date=date).\
        values('id', 'title').annotate(
            read_num=Sum('read_num_obj__read_num')).\
        order_by('-read_num_obj__read_num')
        return one_day_hot_blog_list[:7]

    @classmethod
    def get_7_days_hot_blog_list(cls):
        today = timezone.now().date()
        date = today - timedelta(days=7)
        instances = cls.objects.filter(
            read_num_obj__read_date__lt=today,\
            read_num_obj__read_date__gte=date)
        hot_blog_list = instances.values('id', 'title').\
        annotate(read_num=Sum('read_num_obj__read_num')).\
        order_by('-read_num')
        return hot_blog_list[:7]

    @classmethod
    def use_cache(cls):
        today = timezone.now().date()
        yesterday  = today - timedelta(days=1)
        today_hot_blog_list = cache.get('today_hot_blog_list')
        if today_hot_blog_list is None:
            cache.set('today_hot_blog_list',\
            cls.get_one_day_hot_blog_list(today), settings.CACHES_EXPIRE)
            today_hot_blog_list = cls.get_one_day_hot_blog_list(today)
        else: 
            print('cache')
        yesterday_hot_blog_list = cache.get('yesterday_hot_blog_list')
        if yesterday_hot_blog_list is None:
            cache.set('yesterday_hot_blog_list',\
            cls.get_one_day_hot_blog_list(yesterday), settings.CACHES_EXPIRE)
            yesterday_hot_blog_list = cls.get_one_day_hot_blog_list(yesterday)
            
        hot_blog_list = cache.get('hot_blog_list')
        if hot_blog_list is None:
            cache.set('hot_blog_list',\
            cls.get_7_days_hot_blog_list(), settings.CACHES_EXPIRE)
            hot_blog_list = cls.get_7_days_hot_blog_list()
        return today_hot_blog_list, yesterday_hot_blog_list, hot_blog_list
                    


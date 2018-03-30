from datetime import timedelta
from django.utils import timezone
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

def get_seven_days_read_nums():
        read_date = timezone.now().date()
        date_list = []
        read_num_list = []
        for i in range(6,-1,-1):
            date = read_date - timedelta(days=i)
            date_list.append(date.strftime('%m-%d'))
            global total_nums_by_date
            read_num_set = ReadNums.objects.filter(read_date=date)
            if read_num_set:
                total_nums_by_date = read_num_set.aggregate(read_nums_by_day=\
                    Sum('read_num'))
                read_num_list.append(total_nums_by_date['read_nums_by_day'])
            else:
                read_num_list.append(0)
            
        return read_num_list, date_list
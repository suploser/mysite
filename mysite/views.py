from django.shortcuts import render_to_response
from read_statistics.utils import get_seven_days_read_nums
def home(request):
    read_num_list, date_list = get_seven_days_read_nums()
    context = {}
    context['read_num_list'] = read_num_list
    context['date_list'] = date_list
    return render_to_response('home.html', context=context)
    
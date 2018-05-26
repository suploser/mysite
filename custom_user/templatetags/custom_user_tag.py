from django import template
from custom_user.forms import ForgetPwdForm

register = template.Library()
@register.simple_tag
def get_pwd_form():
    return ForgetPwdForm()
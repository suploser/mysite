from django import template
from custom_user.forms import ForgetPwdForm, ChangePwdForm, ChangeEmailForm

register = template.Library()
@register.simple_tag
def get_pwd_form():
    return ForgetPwdForm()

@register.simple_tag
def get_change_pwd_form():
    return ChangePwdForm()

@register.simple_tag
def get_change_email_form():
    return ChangeEmailForm()

from mysite.forms import loginForm, RegForm

def overall_form(request):
    return {
        'loginForm':loginForm,
        'RegForm':RegForm,
    }
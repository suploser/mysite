from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.CharField(widget=forms.HiddenInput)
    comment_content = forms.CharField(
        widget=CKEditorWidget(config_name='comment_ckeditor'),
        error_messages={'required':'评论内容不能为空!'}
        )

    def __init__(self, *args, **kwords):
        if 'session' in kwords:
            self.session = kwords.pop('session')
        super(CommentForm, self).__init__(*args, **kwords)


    def clean(self):
        #验证登录
        if not self.session.get('username'):
            raise forms.ValidationError('未登录!请登录后评论')
        else:
            user = self.session.get('user')
            username = self.session.get('username')
            password = self.session.get('password')
            User = ContentType.objects.filter(model=user)[1].model_class()
            user = User.objects.filter(username=username, password=password).first()
            self.cleaned_data['user'] = user
        #验证评论对象是否存在
        content_type = self.cleaned_data['content_type']
        object_id = int(self.cleaned_data['object_id'])
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            content_object = model_class.objects.get(id=object_id)
            self.cleaned_data['content_object'] = content_object
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论文章不存在!')

        return self.cleaned_data
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from blog.views import blogs_list
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('blog/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('overall_login/', views.overall_login, name="overall_login"),
    path('overall_regist/', views.overall_regist, name="overall_regist"),
    path('login/',views.login, name='login'),
    path('regist/', views.regist, name='regist'),
    path('confirm/', views.confirm, name='confirm'),
    path('logout/', views.logout, name='logout'),
    path('comment/', include('comment.urls')),
    path('ueditor/', include('ueditor.urls')),
    path('favor/', include('favor.urls')),
]
# 关联MEDIA_URL和MEDIA_ROOT
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


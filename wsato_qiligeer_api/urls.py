from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'create_vm$', views.CreateVm.as_view()), # views.pyで定義するYamabikoクラスを呼び出す
]

urlpatterns = format_suffix_patterns(urlpatterns)

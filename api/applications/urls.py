from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^upload/cover$', views.upload_cover),
    url(r'^upload/banner$', views.upload_banner),
]

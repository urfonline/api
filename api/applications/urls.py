from django.conf.urls import url
from . import views

app_name = 'applications'
urlpatterns = [
    url(r'^upload/cover$', views.upload_cover),
    url(r'^upload/banner$', views.upload_banner),
]

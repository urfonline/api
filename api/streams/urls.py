from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^([-a-zA-Z0-9_]+)/status$', views.get_stream_status)
]

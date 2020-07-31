from django.conf.urls import url
from . import views

app_name = 'streams'
urlpatterns = [
    url(r'^([-a-zA-Z0-9_]+)/status$', views.get_stream_status)
]

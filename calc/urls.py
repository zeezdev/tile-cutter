from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r"^floor/$", floor, name='floor'),
    url(r"^walls/$", walls, name='walls'),
]
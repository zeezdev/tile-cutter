from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r"^floor/$", floor, name='floor'),
    url(r"^walls/$", walls, name='walls'),
    url(r"^one-tile-cost/$", one_tile_cost, name='one_tile_cost'),
]
from django.conf.urls import url

from . import views

app_name = 'lolturbine'
urlpatterns = [
    url('^$', views.index, name = 'index'),
    url('^game/(?P<pk>[0-9]+)/$', views.game, name = 'game'),
    url('^add/$', views.addMap, name = 'addMap'),
#    url('^lobby/$', views.lobby, name = 'lobby'),
]

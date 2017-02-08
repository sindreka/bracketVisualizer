from django.conf.urls import url

from . import views

app_name = 'lolturbine'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^game/(?P<pk>[0-9]+)/$', views.game, name = 'game'),
    url(r'^add/$', views.addMap, name = 'addMap'),
    url(r'^place_troops/(?P<pk>[0-9]+)/(?P<n>[0-9]+)', views.place_troops, name = 'place_troops'),
    url(r'^attack/(?P<pk>[0-9]+)/(?P<a>[0-9]+)/(?P<v>[0-9]+)/$', views.attack, name = 'attack'),
    url(r'^reinforce_battle/(?P<pk>[0-9]+)/(?P<f>[0-9]+)/(?P<t>[0-9]+)', views.reinforce_battle, name = 'reinforce_battle'),
    url(r'^reinforce/(?P<pk>[0-9]+)/(?P<f>[0-9]+)/(?P<t>[0-9]+)', views.reinforce, name = 'reinforce'),
#    url('^lobby/$', views.lobby, name = 'lobby'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.bracketViews, name = 'bracketViews'),
	url(r'^(?P<bracketBatch_batchNumber>[0-9]+)', views.batchViews, name = 'batchViews'),
]

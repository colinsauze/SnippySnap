from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'whoami', views.getUser),
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/create/?$', views.ItemCreate.as_view()),
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/update/(?P<pk>[0-9_a-zA-Z]+)/?$', views.ItemUpdate.as_view()),
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/delete/(?P<pk>[0-9_a-zA-Z]+)/?$', views.ItemDelete.as_view()),
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/(?P<pk>[0-9_a-zA-Z]+)/(?P<fieldname>[a-z_]+)/delete/(?P<itemmodel>[0-9_a-zA-Z]+)/(?P<itempk>[0-9_a-zA-Z]+)/?$', views.M2MItemDelete.as_view()),
    #private get models MUST COME FIRST
    #these are now only used in citations they have been combined for transcription app
    url(r'^(?P<app>[a-z_]+)/(?P<model>private[a-z_]+)/(?P<pk>[0-9_a-zA-Z]+)/?$', views.PrivateItemDetail.as_view()),
    url(r'^(?P<app>[a-z_]+)/(?P<model>private[a-z_]+)/?$', views.PrivateItemList.as_view()),
    #non-private models
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/(?P<pk>[0-9_a-zA-Z]+)/?$', views.ItemDetail.as_view()),
    url(r'^(?P<app>[a-z_]+)/(?P<model>[a-z_]+)/?$', views.ItemList.as_view())

]

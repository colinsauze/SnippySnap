from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'(?P<model>[a-z_]+)/searchfields/?$', views.getSearchFields),
    url(r'(?P<model>[a-z_]+)/searchvalues/?', views.getSearchValues),
    url(r'(?P<select>projectselect)', views.index, name='projectselect'),
    url(r'search/advanced/?', views.search, kwargs={'advanced': True}, name='advancedsearch'),
    url(r'search/?', views.search, name='search'),
    url(r'^(?P<model>[a-z_]+)/results/?$', views.listView, kwargs={'results': True}, name='list'),
    url(r'(?P<model>[a-z_]+)/patristics/?$', views.listView, kwargs={'patristics': True}, name='patristics'),
    #url(r'^login/?$', 'django.contrib.auth.views.login', name='login', kwargs={'template_name': 'citations/login.html'}),
    url(r'^(?P<model>[a-z_]+)/?$', views.listView, kwargs=None, name='list'),
    url(r'(?P<model>[a-z_]+)/edit/?$', views.editItem, name='create'),
    url(r'(?P<model>[a-z_]+)/edit/(?P<id>.+)/?$', views.editItem, name='edit'),
    url(r'(?P<model>[a-z_]+)/delete/(?P<id>.+)/?$', views.deleteItem, name='delete'),
    url(r'(?P<model>[a-z_]+)/(?P<id>.+)/?$', views.itemView, name='single'),

]

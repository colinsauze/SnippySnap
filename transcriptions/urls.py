from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'upload/?', views.upload, name='upload'),
    url(r'search/?', views.search, name='search'),
    url(r'results/?', views.results, name='results'),
    url(r'validate/?', views.validate, name="validate"),
    url(r'index/?', views.index, name="index")#this is for indexing transcriptions perhaps need a better word

]

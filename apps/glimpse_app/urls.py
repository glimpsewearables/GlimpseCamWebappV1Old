from django.conf.urls import url
from . import views


urlpatterns = [
   
    url(r'^$', views.index),
    url(r'^createUser$', views.createUser),
    url(r'^createEvent$', views.createEvent),
    url(r'^registerLoginPage$', views.registerLoginPage),
    url(r'^login$', views.login),
    url(r'^adminLogin$', views.adminLogin),
    url(r'^userPage$', views.userPage),
    url(r'^viewImage$', views.viewImage),
    url(r'^godModeCheck$', views.godModeCheck),
    url(r'^godMode$', views.godMode),
    url(r'^viewUserInfoGodMode/(?P<user_num>\d+)$', views.viewUserInfoGodMode),
    url(r'^deleteImage/(?P<match>.+)/(?P<url>.+)$', views.deleteImage),
    url(r'^deleteUser/(?P<user_id>\d+)$', views.deleteUser),
    url(r'^logout$', views.logout),
    url(r'^updateSqlDatabase$', views.updateSqlDatabase),
]  
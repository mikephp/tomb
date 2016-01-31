from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from . import views

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'djsite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^$', views.home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^throw404/$', views.throw404),
    url(r'^throw500/$', views.throw500),
    url(r'^dump/$', views.dump),
    url('', include(
        'social.apps.django_app.urls', namespace='social')),
    # ^login/(?P<backend>[^/]+)/$ [name='begin']
    # ^complete/(?P<backend>[^/]+)/$ [name='complete']
    # ^disconnect/(?P<backend>[^/]+)/$ [name='disconnect']
    # ^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$ [name='disconnect_individual']
    url(r'^login/$', views.login),
    url(r'^home/$', views.home),
    url(r'^logout/$', views.logout),
    url(r'^register/$', views.register),
    url(r'^active/$', views.active),
    url(r'^ymuser/', include('ymuser.urls')),
)

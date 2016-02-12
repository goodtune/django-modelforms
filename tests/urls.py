from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tests.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^book/(?P<pk>\d+)/$',
        'tests.views.update_book',
        name='update-book'),

    url(r'^unique/book/(?P<pk>\d+)/$',
        'tests.views.unique_update_book',
        name='unique-update-book'),
)

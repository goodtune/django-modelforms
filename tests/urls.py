from django.conf.urls import include, url

from .views import update_book, unique_update_book

urlpatterns = [
    url(r'^book/(?P<pk>\d+)/$', update_book, name='update-book'),
    url(r'^unique/book/(?P<pk>\d+)/$', unique_update_book,
        name='unique-update-book'),
]

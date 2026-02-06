from django.urls import path

from .views import update_book, unique_update_book

urlpatterns = [
    path("book/<int:pk>/", update_book, name="update-book"),
    path("unique/book/<int:pk>/", unique_update_book, name="unique-update-book"),
]

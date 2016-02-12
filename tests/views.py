from django.apps import apps
from django.views.generic import edit
from modelforms.views import UpdateView


class UpdateBook(edit.UpdateView):
    model = apps.get_model('tests', 'Book')
    fields = ('title',)

class UniqueUpdateBook(UpdateView):
    model = apps.get_model('tests', 'Book')
    fields = ('title',)

update_book = UpdateBook.as_view()
unique_update_book = UniqueUpdateBook.as_view()

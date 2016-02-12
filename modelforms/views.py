from django.forms.models import modelform_factory
from django.views.generic import edit

from modelforms.forms import ModelForm
from modelforms.mixins import UniqueTogetherMixin


class UpdateView(edit.UpdateView):
    """
    View for updating an object, with a response rendered by template.
    """
    def get_form_class(self):
        form_class = super(UpdateView, self).get_form_class()

        if issubclass(form_class, UniqueTogetherMixin):
            return form_class

        return modelform_factory(form_class._meta.model,
                                 ModelForm,
                                 fields=self.fields)

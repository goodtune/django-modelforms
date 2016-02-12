from django import forms

from modelforms import mixins


class ModelForm(mixins.UniqueTogetherMixin, forms.ModelForm):
    """
    Extension of the built-in ModelForm that restores sensible validation of
    unique_together constraints on a model.
    """

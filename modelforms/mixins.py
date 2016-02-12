from django.core.exceptions import ValidationError
from django.utils.text import capfirst


class UniqueTogetherMixin(object):
    """
    Add this mixin to a ModelForm to restore sensible validation of
    unique_together constraints on a model.
    """
    def clean(self):
        errors = {}
        model = self._meta.model
        opts = model._meta
        manager = model._default_manager

        try:
            super(UniqueTogetherMixin, self).clean()
        except ValidationError, e:
            e.update_error_dict(errors)

        unique_together = {}
        for together in opts.unique_together:
            for field_name in self._meta.fields:
                if field_name in together:
                    unique_together.setdefault(
                        field_name, set()).update(together)

        queryset = manager.exclude(pk=self.instance.pk)
        for field_name in unique_together:
            kw = dict([
                (f, self.cleaned_data.get(f, getattr(self.instance, f)))
                for f in unique_together[field_name]
            ])
            if queryset.filter(**kw):
                field = opts.get_field(field_name)
                params = {
                    'model': self,
                    'model_class': self._meta.model,
                    'model_name': capfirst(opts.verbose_name),
                    'field_label': field.verbose_name,
                }
                message = field.error_messages['unique'] % params
                errors.setdefault(field_name, []).append(message)

        if errors:
            raise ValidationError(errors)

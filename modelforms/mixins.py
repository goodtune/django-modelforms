from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.utils.text import capfirst


class UniqueTogetherMixin:
    """
    Add this mixin to a ModelForm to restore sensible validation of
    unique_together constraints and UniqueConstraint on a model.

    This handles both the legacy Meta.unique_together and the modern
    Meta.constraints with UniqueConstraint.
    """

    def clean(self):
        errors = {}
        model = self._meta.model
        opts = model._meta
        manager = model._default_manager

        try:
            super().clean()
        except ValidationError as e:
            e.update_error_dict(errors)

        # Collect all unique field combinations from both unique_together
        # and UniqueConstraint definitions
        unique_field_sets = []

        # Legacy unique_together support
        for together in opts.unique_together:
            unique_field_sets.append(tuple(together))

        # Modern UniqueConstraint support (from Meta.constraints)
        for constraint in opts.constraints:
            if isinstance(constraint, UniqueConstraint):
                # Only validate constraints without conditions or expressions
                # Conditional constraints require runtime evaluation
                if (
                    not getattr(constraint, "condition", None)
                    and not getattr(constraint, "expressions", None)
                    and constraint.fields
                ):
                    unique_field_sets.append(tuple(constraint.fields))

        # Build mapping of form fields to their unique constraint groups
        # Use self.fields.keys() to handle fields='__all__' and fields=None
        form_fields = set(self.fields.keys())
        unique_together = {}
        for together in unique_field_sets:
            for field_name in form_fields:
                if field_name in together:
                    unique_together.setdefault(field_name, set()).update(together)

        queryset = manager.exclude(pk=self.instance.pk)
        for field_name in unique_together:
            kw = {
                f: self.cleaned_data.get(f, getattr(self.instance, f, None))
                for f in unique_together[field_name]
            }
            if queryset.filter(**kw).exists():
                field = opts.get_field(field_name)
                params = {
                    "model": self,
                    "model_class": self._meta.model,
                    "model_name": capfirst(opts.verbose_name),
                    "field_label": field.verbose_name,
                }
                message = field.error_messages["unique"] % params
                errors.setdefault(field_name, []).append(message)

        if errors:
            raise ValidationError(errors)

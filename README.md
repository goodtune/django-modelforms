# django-modelforms

[![CI](https://github.com/goodtune/django-modelforms/actions/workflows/ci.yml/badge.svg)](https://github.com/goodtune/django-modelforms/actions/workflows/ci.yml)

This project came about because our reusable administration has to deal with
related models that have `unique_together` constraints (and modern `UniqueConstraint`)
that were not being properly validated by the default implementation.

It occurs because our forms don't show the related field, it's not something we
want the user to be able to edit. This has the nasty side-effect of excluding
the related field from validation checks, so uniqueness (with respect to the
related field) is not tested.

The form therefore validates, and a database update is attempted - only to fail
when integrity constraints are enforced by the backend.

## Installation

```bash
pip install django-modelforms
```

Or with uv:

```bash
uv add django-modelforms
```

## Usage

Simply use `modelforms.forms.ModelForm` instead of `django.forms.ModelForm`:

```python
from modelforms.forms import ModelForm

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'rrp']
```

This will properly validate both legacy `unique_together` constraints and modern
`UniqueConstraint` definitions in your model's `Meta.constraints`.

## Supported Django and Python Versions

- Django 4.2, 5.2, 6.0
- Python 3.10, 3.11, 3.12, 3.13

## Why?

Django bug [#13091](https://code.djangoproject.com/ticket/13091) was filed in
March 2010 and still has not been fixed.

There has been discussion on the mailing lists and a number of patches
proposed, but none have been accepted.

To stop encountering this in our projects we decided to write something generic
that can easily be used without having to wait for an upstream fix.

## Development

This project uses `uv` and `tox` for development:

```bash
# Install development dependencies
uv sync

# Run tests
uv run tox

# Run tests for a specific environment
uv run tox -e py312-django52

# Run linting
uv run tox -e lint
```

## License

BSD-3-Clause

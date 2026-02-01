from django import forms
from django.apps import apps
from django.db.utils import IntegrityError
from django.forms.models import modelform_factory
from test_plus import TestCase

from modelforms.forms import ModelForm


class UniqueTogetherTests(TestCase):
    """Tests for legacy unique_together constraint validation."""

    def setUp(self):
        # obtain the model classes from application registry
        Author = apps.get_model("tests", "Author")
        Book = apps.get_model("tests", "Book")

        # dynamically define our BookForm class, firstly without the mixin and
        # secondly with it to test we solve a problem.
        self.original_form_class = modelform_factory(
            Book, forms.ModelForm, ("title", "rrp")
        )
        self.form_class = modelform_factory(Book, ModelForm, ("title", "rrp"))

        # create some instances to use in tests
        author = Author.objects.create(name="Robert Ludlum")
        self.book1 = author.books.create(
            title="The Bourne Identity",
            rrp="9.20",
        )
        self.book2 = author.books.create(
            title="The Bourne Supremacy",
            rrp="10.50",
        )

    def test_invalid_rrp(self):
        data = {
            "title": self.book2.title,
            "rrp": "1000",
        }

        # the title is still unique, but the rrp is invalid
        form = self.original_form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "rrp": [
                    "Ensure that there are no more than 3 digits before "
                    "the decimal point."
                ],
            },
        )

        # our mixin has not changed default behaviour on this field
        form = self.form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "rrp": [
                    "Ensure that there are no more than 3 digits before "
                    "the decimal point."
                ],
            },
        )

    def test_title_clash(self):
        data = {
            "title": self.book1.title,
            "rrp": "15.95",
        }

        # title must be unique_together with author, title should not be valid
        form = self.original_form_class(data=data, instance=self.book2)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

        # applying mixin proves we're fixing it
        form = self.form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "title": ["Book with this title already exists."],
            },
        )

    def test_invalid_rrp_and_title_clash(self):
        data = {
            "title": self.book1.title,
            "rrp": "1000",
        }

        # title must be unique_together with author, title should not be valid
        form = self.original_form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "rrp": [
                    "Ensure that there are no more than 3 digits before "
                    "the decimal point."
                ],
            },
        )

        # applying mixin proves we're fixing it
        form = self.form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "title": ["Book with this title already exists."],
                "rrp": [
                    "Ensure that there are no more than 3 digits before "
                    "the decimal point."
                ],
            },
        )

    def test_update_view(self):
        data = {
            "title": self.book1.title,
        }
        with self.assertRaises(IntegrityError):
            self.post("update-book", self.book2.pk, data=data)

    def test_unique_update_view(self):
        data = {
            "title": self.book1.title,
        }
        response = self.post("unique-update-book", self.book2.pk, data=data)
        # Check the form has errors via context
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {"title": ["Book with this title already exists."]},
        )


class UniqueConstraintTests(TestCase):
    """Tests for modern UniqueConstraint validation."""

    def setUp(self):
        # obtain the model classes from application registry
        Publisher = apps.get_model("tests", "Publisher")
        Magazine = apps.get_model("tests", "Magazine")

        # dynamically define our MagazineForm class
        self.original_form_class = modelform_factory(
            Magazine, forms.ModelForm, ("title", "issue_number")
        )
        self.form_class = modelform_factory(
            Magazine, ModelForm, ("title", "issue_number")
        )

        # create some instances to use in tests
        publisher = Publisher.objects.create(name="Conde Nast")
        self.magazine1 = Magazine.objects.create(
            title="Vogue",
            publisher=publisher,
            issue_number=1,
        )
        self.magazine2 = Magazine.objects.create(
            title="GQ",
            publisher=publisher,
            issue_number=1,
        )

    def test_title_clash_with_unique_constraint(self):
        """Test that UniqueConstraint validation catches duplicate titles."""
        data = {
            "title": self.magazine1.title,
            "issue_number": 2,
        }

        # Standard Django form doesn't catch the clash
        form = self.original_form_class(data=data, instance=self.magazine2)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

        # Our mixin catches the UniqueConstraint violation
        form = self.form_class(data=data, instance=self.magazine2)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "title": ["Magazine with this title already exists."],
            },
        )

    def test_valid_unique_title(self):
        """Test that valid unique titles pass validation."""
        data = {
            "title": "Wired",  # A new unique title
            "issue_number": 1,
        }

        form = self.form_class(data=data, instance=self.magazine2)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

    def test_same_instance_update(self):
        """Test that updating an instance with its own values is valid."""
        data = {
            "title": self.magazine1.title,
            "issue_number": 2,
        }

        # Updating magazine1 with its own title should be valid
        form = self.form_class(data=data, instance=self.magazine1)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

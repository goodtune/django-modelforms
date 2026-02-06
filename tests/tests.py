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


class FieldsAllTests(TestCase):
    """Tests for forms using fields='__all__'."""

    def setUp(self):
        Author = apps.get_model("tests", "Author")
        Book = apps.get_model("tests", "Book")
        Publisher = apps.get_model("tests", "Publisher")
        Magazine = apps.get_model("tests", "Magazine")

        self.author = Author.objects.create(name="Robert Ludlum")
        self.book1 = self.author.books.create(title="The Bourne Identity", rrp="9.20")
        self.book2 = self.author.books.create(title="The Bourne Supremacy", rrp="10.50")

        self.publisher = Publisher.objects.create(name="Conde Nast")
        self.magazine1 = Magazine.objects.create(
            title="Vogue", publisher=self.publisher, issue_number=1
        )
        self.magazine2 = Magazine.objects.create(
            title="GQ", publisher=self.publisher, issue_number=1
        )

        # Create form classes with fields='__all__'
        class BookFormAll(ModelForm):
            class Meta:
                model = Book
                fields = "__all__"

        class MagazineFormAll(ModelForm):
            class Meta:
                model = Magazine
                fields = "__all__"

        self.book_form_class = BookFormAll
        self.magazine_form_class = MagazineFormAll

    def test_unique_together_with_fields_all(self):
        """Test unique_together validation works with fields='__all__'."""
        data = {
            "title": self.book1.title,
            "author": self.author.pk,
            "rrp": "15.95",
        }

        form = self.book_form_class(data=data, instance=self.book2)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_unique_constraint_with_fields_all(self):
        """Test UniqueConstraint validation works with fields='__all__'."""
        data = {
            "title": self.magazine1.title,
            "publisher": self.publisher.pk,
            "issue_number": 2,
        }

        form = self.magazine_form_class(data=data, instance=self.magazine2)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_valid_data_with_fields_all(self):
        """Test that valid data passes with fields='__all__'."""
        data = {
            "title": "New Unique Title",
            "author": self.author.pk,
            "rrp": "15.95",
        }

        form = self.book_form_class(data=data, instance=self.book2)
        self.assertTrue(form.is_valid())


class AllConstraintFieldsTests(TestCase):
    """Tests for forms that include all fields in the constraint."""

    def setUp(self):
        Publisher = apps.get_model("tests", "Publisher")
        Magazine = apps.get_model("tests", "Magazine")

        self.publisher1 = Publisher.objects.create(name="Conde Nast")
        self.publisher2 = Publisher.objects.create(name="Hearst")
        self.magazine1 = Magazine.objects.create(
            title="Vogue", publisher=self.publisher1, issue_number=1
        )
        self.magazine2 = Magazine.objects.create(
            title="GQ", publisher=self.publisher1, issue_number=1
        )

        # Form that includes publisher (all constraint fields present)
        self.form_class = modelform_factory(
            Magazine, ModelForm, ("title", "publisher", "issue_number")
        )

    def test_clash_with_all_constraint_fields_in_form(self):
        """Test validation when all constraint fields are in the form."""
        data = {
            "title": self.magazine1.title,
            "publisher": self.publisher1.pk,
            "issue_number": 2,
        }

        form = self.form_class(data=data, instance=self.magazine2)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_same_title_different_publisher(self):
        """Test that same title with different publisher is valid."""
        data = {
            "title": self.magazine1.title,  # Same title as magazine1
            "publisher": self.publisher2.pk,  # Different publisher
            "issue_number": 1,
        }

        form = self.form_class(data=data, instance=self.magazine2)
        self.assertTrue(form.is_valid())

    def test_changing_publisher_to_cause_clash(self):
        """Test changing publisher to one where title already exists."""
        # First create a magazine with publisher2
        Magazine = apps.get_model("tests", "Magazine")
        magazine3 = Magazine.objects.create(
            title="Vogue", publisher=self.publisher2, issue_number=1
        )

        # Now try to change magazine2's publisher to publisher2 with title Vogue
        data = {
            "title": "Vogue",
            "publisher": self.publisher2.pk,
            "issue_number": 2,
        }

        form = self.form_class(data=data, instance=self.magazine2)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class NewInstanceCreationTests(TestCase):
    """Tests for creating new instances (no pk)."""

    def setUp(self):
        Author = apps.get_model("tests", "Author")
        Book = apps.get_model("tests", "Book")
        Publisher = apps.get_model("tests", "Publisher")
        Magazine = apps.get_model("tests", "Magazine")

        self.author = Author.objects.create(name="Robert Ludlum")
        self.book1 = self.author.books.create(title="The Bourne Identity", rrp="9.20")

        self.publisher = Publisher.objects.create(name="Conde Nast")
        self.magazine1 = Magazine.objects.create(
            title="Vogue", publisher=self.publisher, issue_number=1
        )

        # Form classes for creation
        class BookForm(ModelForm):
            class Meta:
                model = Book
                fields = "__all__"

        class MagazineForm(ModelForm):
            class Meta:
                model = Magazine
                fields = "__all__"

        self.book_form_class = BookForm
        self.magazine_form_class = MagazineForm
        self.Book = Book
        self.Magazine = Magazine

    def test_create_with_unique_together_clash(self):
        """Test creating new instance with unique_together violation."""
        data = {
            "title": self.book1.title,  # Same title as existing book
            "author": self.author.pk,  # Same author
            "rrp": "15.95",
        }

        # Create form without instance (new object)
        form = self.book_form_class(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_create_with_unique_constraint_clash(self):
        """Test creating new instance with UniqueConstraint violation."""
        data = {
            "title": self.magazine1.title,  # Same title as existing magazine
            "publisher": self.publisher.pk,  # Same publisher
            "issue_number": 2,
        }

        # Create form without instance (new object)
        form = self.magazine_form_class(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_create_valid_unique_together(self):
        """Test creating new instance with valid unique_together."""
        data = {
            "title": "New Unique Book",
            "author": self.author.pk,
            "rrp": "15.95",
        }

        form = self.book_form_class(data=data)
        self.assertTrue(form.is_valid())

    def test_create_valid_unique_constraint(self):
        """Test creating new instance with valid UniqueConstraint."""
        data = {
            "title": "New Unique Magazine",
            "publisher": self.publisher.pk,
            "issue_number": 1,
        }

        form = self.magazine_form_class(data=data)
        self.assertTrue(form.is_valid())

    def test_create_same_title_different_relation(self):
        """Test creating with same title but different related object is valid."""
        Author = apps.get_model("tests", "Author")
        new_author = Author.objects.create(name="John Grisham")

        data = {
            "title": self.book1.title,  # Same title
            "author": new_author.pk,  # Different author
            "rrp": "15.95",
        }

        form = self.book_form_class(data=data)
        self.assertTrue(form.is_valid())

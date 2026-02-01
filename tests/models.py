from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    """Test model using legacy unique_together."""

    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    rrp = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = (("title", "author"),)


class Publisher(models.Model):
    name = models.CharField(max_length=100)


class Magazine(models.Model):
    """Test model using modern UniqueConstraint."""

    title = models.CharField(max_length=100)
    publisher = models.ForeignKey(
        Publisher, related_name="magazines", on_delete=models.CASCADE
    )
    issue_number = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "publisher"],
                name="unique_magazine_title_per_publisher",
            ),
        ]

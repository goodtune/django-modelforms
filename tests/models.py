from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name='books')
    rrp = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = (
            ('title', 'author'),
            # ('title', 'rrp'),
        )

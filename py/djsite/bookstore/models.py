from django.db import models

# Create your models here.

from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    website = models.URLField()

    def __unicode__(self):
        return u'publisher(%s @ %s)' % (self.name, self.website)

    class Meta:
        # order by 'name' or '-name'
        # same as Publisher.objects.order_by('name')
        ordering = ['name']

class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(blank = True)

    def __unicode__(self):
        return u'auth(%s %s @ %s)' % (self.first_name, self.last_name, self.email)

class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateField(blank = True, null = True)

    def __unicode__(self):
        return u'book(%s by %s @ %s)' % (self.title, self.publisher, self.publication_date)

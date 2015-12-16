from django.contrib import admin
from .models import *

# Register your models here.

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name')

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'publication_date')
    list_filter = ('publication_date',) # filter by which fields.
    date_hierarchy = 'publication_date'
    ordering = ('-publication_date',)
    fields = ('title', 'authors', 'publisher', 'publication_date') # fields can be edited.
    filter_horizontal = ('authors',) # recommended for selecting multiple fields.
    raw_id_fields = ('publisher',)

admin.site.register(Book, BookAdmin)
admin.site.register(Publisher)
admin.site.register(Author, AuthorAdmin)

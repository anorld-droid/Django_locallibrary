from django.contrib import admin
from .models import Author, Language, Genre, Book, Bookinstance
# Register your models here.

# admin.site.register(Author)
# Define the admin class


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)
# admin.site.register(Language)
admin.site.register(Genre)
# admin.site.register(Book)
# Define a book class and
# Register the admin classes for Book using the decorator


class BookInstanceInline(admin.TabularInline):
    model = Bookinstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]

# admin.site.register(Bookinstance)
# Define BookInstance class and
# Register the admin classes for bookInstance using the decorator


@admin.register(Bookinstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

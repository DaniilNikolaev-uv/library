from django.contrib import admin

from .models import Author, Book, Category, Publisher


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "middle_name", "date_of_birth", "date_of_death"]
    list_filter = ["date_of_birth"]
    search_fields = ["first_name", "last_name", "middle_name"]
    ordering = ["last_name", "first_name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    list_filter = ["parent"]
    search_fields = ["name"]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "city"]
    list_filter = ["country"]
    search_fields = ["name", "country", "city"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "isbn", "get_authors", "publisher"]
    list_filter = ["year", "language", "categories", "publisher"]
    search_fields = ["title", "subtitle", "isbn", "authors__last_name"]
    filter_horizontal = ["authors", "categories"]
    ordering = ["title"]

    def get_authors(self, obj):
        return ", ".join(str(a) for a in obj.authors.all())
    get_authors.short_description = "Авторы"

from django.contrib import admin

from reviews.models import Category, Genre, Title, TitleGenre


class TitleGenreAdmin(admin.TabularInline):
    model = TitleGenre
    extra = 1


class TitleAdmin(admin.ModelAdmin):
    inlines = (TitleGenreAdmin,)


admin.site.register(Title, TitleAdmin)
admin.site.register(Category)
admin.site.register(Genre)

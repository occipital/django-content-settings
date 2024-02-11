from django.contrib import admin
from .models import Artist, Song


class SongInline(admin.TabularInline):
    model = Song
    extra = 1


class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [SongInline]


class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist")
    list_filter = ("artist",)
    search_fields = ("title", "artist__name")


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)

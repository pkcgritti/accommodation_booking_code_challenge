from django.contrib import admin

from .models import Accommodation


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "price", "type"]
    list_filter = ["location", "type"]
    search_fields = ["name", "location", "type"]

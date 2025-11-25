from django.contrib import admin

from .models import Booking, VoiceNote


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["accommodation", "guest_name", "start_date", "end_date"]
    list_filter = ["start_date", "end_date"]
    search_fields = ["guest_name", "accommodation__name"]
    date_hierarchy = "start_date"


@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = ["booking", "transcript", "status"]
    list_filter = ["status"]
    search_fields = ["transcript"]

from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "srcaddr", "dstaddr", "action", "starttime", "endtime", "file_name")
    search_fields = ("srcaddr", "dstaddr", "action", "account_id", "instance_id", "file_name")
    list_filter = ("action", "protocol")

# Register your models here.

# Register your models here.
from django.contrib import admin
from kidKnowGarden.models import *

admin.site.register(
    Rooms,
    list_display=["id", "title", "staff_only"],
    list_display_links=["id", "title"],
)
admin.site.register(Question)
admin.site.register(ContestScore)
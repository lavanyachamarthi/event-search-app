from django.urls import path
from .views import upload_files, search_events, health

urlpatterns = [
    path("upload/", upload_files, name="upload"),
    path("search/", search_events, name="search"),
    path("health/", health, name="health"),
]





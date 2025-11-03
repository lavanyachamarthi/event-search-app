from django.urls import path
from .views import UploadEventsView, SearchEventsView


urlpatterns = [
    path('upload/', UploadEventsView.as_view(), name='upload-events'),
    path('search/', SearchEventsView.as_view(), name='search-events'),
]





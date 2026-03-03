from django.urls import path

from .views.dashboard import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
]

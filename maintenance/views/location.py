from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from maintenance.forms import LocationForm
from maintenance.models import Location


@login_required
def location_list(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.annotate(
        asset_count=Count("asset", distinct=True),
        schedule_count=Count("schedule", distinct=True),
        project_count=Count("project", distinct=True),
        issue_count=Count("issue", distinct=True),
    )
    return render(request, "locations/list.html", {"locations": locations})


@login_required
def location_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("location_list")
    else:
        form = LocationForm()
    return render(request, "locations/form.html", {"form": form, "editing": False})


@login_required
def location_edit(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect("location_list")
    else:
        form = LocationForm(instance=location)
    return render(request, "locations/form.html", {"form": form, "location": location, "editing": True})


@login_required
@require_POST
def location_delete(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    location.delete()  # SET_NULL on all FKs — safe to delete
    return redirect("location_list")

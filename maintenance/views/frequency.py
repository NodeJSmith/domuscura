from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from maintenance.forms import FrequencyForm
from maintenance.models import Frequency


@login_required
def frequency_list(request: HttpRequest) -> HttpResponse:
    frequencies = Frequency.objects.all()
    return render(request, "frequencies/list.html", {"frequencies": frequencies})


@login_required
def frequency_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FrequencyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("frequency_list")
    else:
        form = FrequencyForm()
    return render(request, "frequencies/form.html", {"form": form, "editing": False})


@login_required
def frequency_edit(request: HttpRequest, pk: int) -> HttpResponse:
    frequency = get_object_or_404(Frequency, pk=pk)
    if request.method == "POST":
        form = FrequencyForm(request.POST, instance=frequency)
        if form.is_valid():
            form.save()
            return redirect("frequency_list")
    else:
        form = FrequencyForm(instance=frequency)
    return render(request, "frequencies/form.html", {"form": form, "frequency": frequency, "editing": True})


@login_required
@require_POST
def frequency_delete(request: HttpRequest, pk: int) -> HttpResponse:
    frequency = get_object_or_404(Frequency, pk=pk)
    try:
        frequency.delete()
    except Exception:
        # PROTECT prevents deletion if schedules use this frequency
        pass
    return redirect("frequency_list")

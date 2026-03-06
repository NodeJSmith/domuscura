from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from maintenance.forms import WorkLogForm
from maintenance.models import Schedule, WorkLog


@login_required
@require_POST
def quick_log(request: HttpRequest, schedule_id: int) -> HttpResponse:
    """Mark a schedule as done right now, with no extra details."""
    schedule = get_object_or_404(Schedule, pk=schedule_id)

    work_log = WorkLog.objects.create(
        schedule=schedule,
        completed_at=timezone.now(),
        performed_by="self",
    )

    # Return updated schedule card partial for HTMX swap
    schedule.schedule_status = schedule.compute_status(work_log.completed_at)
    return render(request, "partials/schedule_card.html", {"schedule": schedule})


@login_required
def log_work_form(request: HttpRequest, schedule_id: int | None = None) -> HttpResponse:
    """Show or process the full work log form."""
    schedule = None
    if schedule_id:
        schedule = get_object_or_404(Schedule, pk=schedule_id)

    if request.method == "POST":
        form = WorkLogForm(request.POST)
        if form.is_valid():
            work_log = form.save()

            # If this was for a schedule, return updated card
            if work_log.schedule:
                work_log.schedule.schedule_status = work_log.schedule.compute_status(
                    work_log.completed_at
                )
                return render(
                    request,
                    "partials/schedule_card.html",
                    {"schedule": work_log.schedule},
                )

            # Otherwise, return success
            return HttpResponse(
                '<p role="alert">Work logged successfully.</p>',
                headers={"HX-Trigger": "workLogCreated"},
            )
    else:
        initial = {}
        if schedule:
            initial["schedule"] = schedule
        form = WorkLogForm(initial=initial)

    return render(request, "partials/work_log_form.html", {
        "form": form,
        "schedule": schedule,
    })

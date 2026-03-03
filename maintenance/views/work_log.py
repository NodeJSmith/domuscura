from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from maintenance.forms import WorkLogForm
from maintenance.models import Schedule, WorkLog


@require_POST
def quick_log(request, schedule_id):
    """Mark a schedule as done right now, with no extra details."""
    schedule = get_object_or_404(Schedule, pk=schedule_id)

    WorkLog.objects.create(
        schedule=schedule,
        completed_at=timezone.now(),
        performed_by="self",
    )

    # Return updated schedule card partial for HTMX swap
    # Re-fetch to get fresh last_completed
    last = WorkLog.objects.filter(schedule=schedule).order_by("-completed_at").first()
    schedule.last_completed = last.completed_at if last else None
    schedule.status = "ok"
    schedule.days_since_last = 0
    schedule.next_due_date = (
        timezone.now() + timezone.timedelta(days=schedule.frequency_days)
    ).date()
    schedule.days_until_due = schedule.frequency_days

    return render(request, "partials/schedule_card.html", {"schedule": schedule})


def log_work_form(request, schedule_id=None):
    """Show or process the full work log form."""
    schedule = None
    if schedule_id:
        schedule = get_object_or_404(Schedule, pk=schedule_id)

    if request.method == "POST":
        form = WorkLogForm(request.POST)
        if form.is_valid():
            work_log = form.save(commit=False)
            if not work_log.completed_at:
                work_log.completed_at = timezone.now()
            work_log.save()

            # If this was for a schedule, return updated card
            if work_log.schedule:
                sched = work_log.schedule
                sched.last_completed = work_log.completed_at
                sched.status = "ok"
                sched.days_since_last = 0
                sched.next_due_date = (
                    work_log.completed_at + timezone.timedelta(days=sched.frequency_days)
                ).date()
                sched.days_until_due = sched.frequency_days

                return render(request, "partials/schedule_card.html", {"schedule": sched})

            # Otherwise, redirect or return success
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

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from maintenance.forms import ScheduleForm
from maintenance.models import Location, Schedule


def _annotate_status(queryset):
    """Annotate a queryset of schedules with last_completed and compute status."""
    now = timezone.now()
    queryset = Schedule.annotate_last_completed(queryset)

    result = []
    for s in queryset:
        s.compute_status(s.last_completed, now=now)
        result.append(s)
    return result


def _apply_filters(qs, params):
    """Apply query-string filters to a Schedule queryset."""
    active_filter = params.get("active", "active")
    if active_filter == "active":
        qs = qs.filter(active=True)
    elif active_filter == "inactive":
        qs = qs.filter(active=False)

    category = params.get("category", "")
    if category:
        qs = qs.filter(category=category)

    location_id = params.get("location", "")
    if location_id:
        qs = qs.filter(
            Q(location_id=location_id) | Q(asset__location_id=location_id)
        )

    priority = params.get("priority", "")
    if priority:
        qs = qs.filter(priority=priority)

    search = params.get("q", "").strip()
    if search:
        qs = qs.filter(name__icontains=search)

    return qs


SORT_KEYS = {
    "name": lambda s: s.name.lower(),
    "priority": lambda s: {"critical": 0, "high": 1, "normal": 2, "low": 3}.get(s.priority, 2),
    "frequency": lambda s: s.frequency_days,
    "status": lambda s: {"overdue": 0, "due_soon": 1, "never_done": 2, "ok": 3}.get(s.status, 4),
    "category": lambda s: (s.effective_category or "zzz").lower(),
}


def _sort_schedules(schedules, sort_param):
    """Sort a list of schedules by the given sort parameter (prefix '-' for descending)."""
    reverse = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")

    if sort_key in SORT_KEYS:
        schedules.sort(key=SORT_KEYS[sort_key], reverse=reverse)

    return schedules


@login_required
def schedule_list(request):
    qs = Schedule.objects.select_related("asset", "location", "asset__location")
    qs = _apply_filters(qs, request.GET)

    # Annotate with status
    schedules = _annotate_status(qs)

    # Filter by computed status
    status_filter = request.GET.get("status", "")
    if status_filter:
        schedules = [s for s in schedules if s.status == status_filter]

    # Sort
    sort = request.GET.get("sort", "name")
    _sort_schedules(schedules, sort)

    # Filter options for the template
    categories = sorted(set(
        s.effective_category for s in Schedule.objects.select_related("asset").all()
        if s.effective_category
    ))
    locations = Location.objects.all()

    context = {
        "schedules": schedules,
        "categories": categories,
        "locations": locations,
        "priorities": Schedule.PRIORITY_CHOICES,
        "filters": {
            "category": request.GET.get("category", ""),
            "location": request.GET.get("location", ""),
            "priority": request.GET.get("priority", ""),
            "status": status_filter,
            "active": request.GET.get("active", "active"),
            "q": request.GET.get("q", "").strip(),
            "sort": sort,
        },
    }

    if request.headers.get("HX-Request"):
        return render(request, "partials/schedule_list_body.html", context)

    return render(request, "schedules/list.html", context)


@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(
        Schedule.objects.select_related("asset", "location", "asset__location"),
        pk=pk,
    )

    last_log = schedule.work_logs.order_by("-completed_at").first()
    last_completed = last_log.completed_at if last_log else None
    schedule.compute_status(last_completed)

    work_logs = schedule.work_logs.order_by("-completed_at")[:20]

    context = {
        "schedule": schedule,
        "work_logs": work_logs,
    }
    return render(request, "schedules/detail.html", context)


@login_required
def schedule_create(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            return redirect("schedule_detail", pk=schedule.pk)
    else:
        form = ScheduleForm()

    return render(request, "schedules/form.html", {"form": form, "editing": False})


@login_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("schedule_detail", pk=schedule.pk)
    else:
        form = ScheduleForm(instance=schedule)

    return render(request, "schedules/form.html", {
        "form": form,
        "schedule": schedule,
        "editing": True,
    })


@login_required
@require_POST
def schedule_toggle_active(request, pk):
    """HTMX endpoint to toggle a schedule's active state."""
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.active = not schedule.active
    schedule.save(update_fields=["active"])

    if request.headers.get("HX-Request"):
        # Return the updated row
        last_log = schedule.work_logs.order_by("-completed_at").first()
        last_completed = last_log.completed_at if last_log else None
        schedule.compute_status(last_completed)
        return render(request, "partials/schedule_row.html", {"schedule": schedule})

    return redirect("schedule_list")

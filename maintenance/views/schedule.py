from datetime import timedelta

from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from maintenance.forms import ScheduleForm
from maintenance.models import Location, Schedule, WorkLog


def _annotate_status(schedules):
    """Annotate a queryset of schedules with last_completed and compute status."""
    now = timezone.now()
    last_completion = (
        WorkLog.objects.filter(schedule=OuterRef("pk"))
        .order_by("-completed_at")
        .values("completed_at")[:1]
    )
    schedules = schedules.annotate(last_completed=Subquery(last_completion))

    result = []
    for s in schedules:
        if s.last_completed is None:
            s.status = "never_done"
            s.days_since_last = None
            s.next_due_date = None
        else:
            days_since = (now - s.last_completed).days
            s.days_since_last = days_since
            s.next_due_date = (s.last_completed + timedelta(days=s.frequency_days)).date()
            if days_since > s.frequency_days:
                s.status = "overdue"
                s.days_overdue = days_since - s.frequency_days
            elif days_since > s.frequency_days * 0.85:
                s.status = "due_soon"
                s.days_until_due = s.frequency_days - days_since
            else:
                s.status = "ok"
                s.days_until_due = s.frequency_days - days_since
        result.append(s)
    return result


def schedule_list(request):
    qs = Schedule.objects.select_related("asset", "location", "asset__location")

    # Filters
    category = request.GET.get("category", "")
    location_id = request.GET.get("location", "")
    priority = request.GET.get("priority", "")
    status_filter = request.GET.get("status", "")
    active_filter = request.GET.get("active", "active")
    search = request.GET.get("q", "").strip()

    if active_filter == "active":
        qs = qs.filter(active=True)
    elif active_filter == "inactive":
        qs = qs.filter(active=False)
    # "all" shows both

    if category:
        qs = qs.filter(category=category)
    if location_id:
        qs = qs.filter(
            Q(location_id=location_id) | Q(asset__location_id=location_id)
        )
    if priority:
        qs = qs.filter(priority=priority)
    if search:
        qs = qs.filter(name__icontains=search)

    # Annotate with status
    schedules = _annotate_status(qs)

    # Filter by computed status
    if status_filter:
        schedules = [s for s in schedules if s.status == status_filter]

    # Sort
    sort = request.GET.get("sort", "name")
    reverse = sort.startswith("-")
    sort_key = sort.lstrip("-")

    sort_map = {
        "name": lambda s: s.name.lower(),
        "priority": lambda s: {"critical": 0, "high": 1, "normal": 2, "low": 3}.get(s.priority, 2),
        "frequency": lambda s: s.frequency_days,
        "status": lambda s: {"overdue": 0, "due_soon": 1, "never_done": 2, "ok": 3}.get(s.status, 4),
        "category": lambda s: (s.effective_category or "zzz").lower(),
    }

    if sort_key in sort_map:
        schedules.sort(key=sort_map[sort_key], reverse=reverse)

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
            "category": category,
            "location": location_id,
            "priority": priority,
            "status": status_filter,
            "active": active_filter,
            "q": search,
            "sort": sort,
        },
    }

    if request.headers.get("HX-Request"):
        return render(request, "partials/schedule_list_body.html", context)

    return render(request, "schedules/list.html", context)


def schedule_detail(request, pk):
    schedule = get_object_or_404(
        Schedule.objects.select_related("asset", "location", "asset__location"),
        pk=pk,
    )

    # Status calculation
    last_log = schedule.work_logs.order_by("-completed_at").first()
    now = timezone.now()
    if last_log is None:
        schedule.status = "never_done"
        schedule.last_completed = None
        schedule.days_since_last = None
        schedule.next_due_date = None
    else:
        schedule.last_completed = last_log.completed_at
        days_since = (now - last_log.completed_at).days
        schedule.days_since_last = days_since
        schedule.next_due_date = (last_log.completed_at + timedelta(days=schedule.frequency_days)).date()
        if days_since > schedule.frequency_days:
            schedule.status = "overdue"
            schedule.days_overdue = days_since - schedule.frequency_days
        elif days_since > schedule.frequency_days * 0.85:
            schedule.status = "due_soon"
            schedule.days_until_due = schedule.frequency_days - days_since
        else:
            schedule.status = "ok"
            schedule.days_until_due = schedule.frequency_days - days_since

    # Work log history
    work_logs = schedule.work_logs.order_by("-completed_at")[:20]

    context = {
        "schedule": schedule,
        "work_logs": work_logs,
    }
    return render(request, "schedules/detail.html", context)


def schedule_create(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            return redirect("schedule_detail", pk=schedule.pk)
    else:
        form = ScheduleForm()

    return render(request, "schedules/form.html", {"form": form, "editing": False})


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


def schedule_toggle_active(request, pk):
    """HTMX endpoint to toggle a schedule's active state."""
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.active = not schedule.active
    schedule.save(update_fields=["active"])

    if request.headers.get("HX-Request"):
        # Return the updated row
        _annotate_single(schedule)
        return render(request, "partials/schedule_row.html", {"schedule": schedule})

    return redirect("schedule_list")


def _annotate_single(schedule):
    """Annotate a single schedule instance with status info."""
    now = timezone.now()
    last_log = schedule.work_logs.order_by("-completed_at").first()
    if last_log is None:
        schedule.last_completed = None
        schedule.status = "never_done"
        schedule.days_since_last = None
        schedule.next_due_date = None
    else:
        schedule.last_completed = last_log.completed_at
        days_since = (now - last_log.completed_at).days
        schedule.days_since_last = days_since
        schedule.next_due_date = (last_log.completed_at + timedelta(days=schedule.frequency_days)).date()
        if days_since > schedule.frequency_days:
            schedule.status = "overdue"
            schedule.days_overdue = days_since - schedule.frequency_days
        elif days_since > schedule.frequency_days * 0.85:
            schedule.status = "due_soon"
            schedule.days_until_due = schedule.frequency_days - days_since
        else:
            schedule.status = "ok"
            schedule.days_until_due = schedule.frequency_days - days_since

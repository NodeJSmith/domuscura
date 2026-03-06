from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import Category, Project, Schedule
from maintenance.views.schedule import _annotate_status

_PRIORITY_ORDER: dict[str, int] = {"critical": 0, "high": 1, "normal": 2, "low": 3}


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    now = timezone.now()
    today = now.date()

    qs = Schedule.objects.filter(active=True).select_related(
        "asset", "location", "asset__location", "frequency", "category", "asset__category"
    )

    # Filters
    priority_filter = request.GET.get("priority", "")
    category_filter = request.GET.get("category", "")
    sort = request.GET.get("sort", "")

    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if category_filter:
        qs = qs.filter(category__name=category_filter)

    # Categorize by status
    overdue: list[Schedule] = []
    due_soon: list[Schedule] = []
    never_done: list[Schedule] = []
    ok: list[Schedule] = []

    for s in _annotate_status(qs):
        status = s.schedule_status.status
        if status == "never_done":
            never_done.append(s)
        elif status == "overdue":
            overdue.append(s)
        elif status == "due_soon":
            due_soon.append(s)
        else:
            ok.append(s)

    # Sort within sections
    if sort == "priority":
        for lst in (overdue, due_soon, never_done):
            lst.sort(key=lambda s: _PRIORITY_ORDER.get(s.priority, 2))
    elif sort == "name":
        for lst in (overdue, due_soon, never_done):
            lst.sort(key=lambda s: s.name.lower())
    else:
        # Default: overdue by urgency, due_soon by soonest, never_done by priority
        overdue.sort(key=lambda s: s.schedule_status.days_overdue, reverse=True)
        due_soon.sort(key=lambda s: s.schedule_status.days_until_due)
        never_done.sort(key=lambda s: _PRIORITY_ORDER.get(s.priority, 2))

    # Categories for filter dropdown
    categories = Category.objects.values_list("name", flat=True)

    # Active projects (not done/cancelled)
    projects = (
        Project.objects.exclude(status__in=["done", "cancelled"])
        .select_related("asset", "location")
        .order_by("target_date")
    )
    active_projects = []
    for p in projects:
        p.effective_status_display = p.effective_status
        active_projects.append(p)

    context = {
        "overdue": overdue,
        "due_soon": due_soon,
        "never_done": never_done,
        "ok": ok,
        "projects": active_projects,
        "total_active": len(overdue) + len(due_soon) + len(never_done) + len(ok),
        "today": today,
        "categories": categories,
        "filters": {"priority": priority_filter, "category": category_filter, "sort": sort},
    }

    return render(request, "dashboard.html", context)

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import Project, Schedule
from maintenance.views.schedule import _annotate_status


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    now = timezone.now()
    today = now.date()

    qs = (
        Schedule.objects.filter(active=True)
        .select_related("asset", "location", "asset__location")
    )

    # Categorize schedules by status
    overdue = []
    due_soon = []
    never_done = []
    ok = []

    for s in _annotate_status(qs):
        if s.schedule_status.status == "never_done":
            never_done.append(s)
        elif s.schedule_status.status == "overdue":
            overdue.append(s)
        elif s.schedule_status.status == "due_soon":
            due_soon.append(s)
        else:
            ok.append(s)

    # Sort: overdue by most overdue first, due_soon by soonest first
    overdue.sort(key=lambda s: s.schedule_status.days_overdue, reverse=True)
    due_soon.sort(key=lambda s: s.schedule_status.days_until_due)

    # Sort never_done by priority (critical first)
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    never_done.sort(key=lambda s: priority_order.get(s.priority, 2))

    # Active projects (not done/cancelled)
    projects = (
        Project.objects.exclude(status__in=["done", "cancelled"])
        .select_related("asset", "location")
        .order_by("target_date")
    )

    # Annotate projects with effective status
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
    }

    return render(request, "dashboard.html", context)

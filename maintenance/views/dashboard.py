from django.db.models import Subquery, OuterRef
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import Schedule, Project, WorkLog


def dashboard(request):
    now = timezone.now()
    today = now.date()

    # Get the last completed_at for each active schedule
    last_completion = (
        WorkLog.objects.filter(schedule=OuterRef("pk"))
        .order_by("-completed_at")
        .values("completed_at")[:1]
    )

    schedules = (
        Schedule.objects.filter(active=True)
        .annotate(last_completed=Subquery(last_completion))
        .select_related("asset", "location", "asset__location")
    )

    # Categorize schedules by status
    overdue = []
    due_soon = []
    never_done = []
    ok = []

    for s in schedules:
        s.compute_status(s.last_completed, now=now)
        if s.status == "never_done":
            never_done.append(s)
        elif s.status == "overdue":
            overdue.append(s)
        elif s.status == "due_soon":
            due_soon.append(s)
        else:
            ok.append(s)

    # Sort: overdue by most overdue first, due_soon by soonest first
    overdue.sort(key=lambda s: s.days_overdue, reverse=True)
    due_soon.sort(key=lambda s: s.days_until_due)

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

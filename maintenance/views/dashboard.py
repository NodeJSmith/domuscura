from datetime import timedelta

from django.db.models import Max, Subquery, OuterRef, CharField, DateTimeField
from django.db.models.functions import Now
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
        if s.last_completed is None:
            s.status = "never_done"
            s.days_since_last = None
            s.next_due_date = None
            never_done.append(s)
        else:
            completed_date = s.last_completed
            if timezone.is_aware(completed_date):
                completed_date = completed_date
            days_since = (now - completed_date).days
            s.days_since_last = days_since
            s.next_due_date = (completed_date + timedelta(days=s.frequency_days)).date()

            if days_since > s.frequency_days:
                s.status = "overdue"
                s.days_overdue = days_since - s.frequency_days
                overdue.append(s)
            elif days_since > s.frequency_days * 0.85:
                s.status = "due_soon"
                s.days_until_due = s.frequency_days - days_since
                due_soon.append(s)
            else:
                s.status = "ok"
                s.days_until_due = s.frequency_days - days_since
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
        if p.status == "someday":
            p.effective_status_display = "someday"
        elif p.target_date and p.target_date < today:
            p.effective_status_display = "overdue"
        elif p.target_date and (p.target_date - today).days <= 14:
            p.effective_status_display = "due_soon"
        else:
            p.effective_status_display = p.status
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

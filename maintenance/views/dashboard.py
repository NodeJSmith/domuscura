from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import Category, Frequency, Project, Schedule
from maintenance.views.schedule import _annotate_status

_PRIORITY_ORDER: dict[str, int] = {"critical": 0, "high": 1, "normal": 2, "low": 3}
_IMPACT_ORDER: dict[str, int] = {"safety": 0, "protective": 1, "efficiency": 2, "comfort": 3, "cosmetic": 4}


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
    impact_filter = request.GET.get("impact", "")
    frequency_filter = request.GET.get("frequency", "")
    show = request.GET.get("show", "action_needed")
    sort = request.GET.get("sort", "")

    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if category_filter:
        qs = qs.filter(category__name=category_filter)
    if impact_filter:
        qs = qs.filter(impact=impact_filter)
    if frequency_filter:
        qs = qs.filter(frequency_id=frequency_filter)

    all_schedules = list(_annotate_status(qs))
    total_active = len(all_schedules)

    # Hide up-to-date rows unless user asks for all
    if show == "action_needed":
        all_schedules = [s for s in all_schedules if s.schedule_status.status != "ok"]

    # Sort
    _STATUS_ORDER: dict[str, int] = {"overdue": 0, "due_soon": 1, "never_done": 2, "ok": 3}
    sort_key = sort.lstrip("-")

    if sort_key == "priority":
        all_schedules.sort(key=lambda s: _PRIORITY_ORDER.get(s.priority, 2))
    elif sort_key == "name":
        all_schedules.sort(key=lambda s: s.name.lower())
    elif sort_key == "impact":
        all_schedules.sort(key=lambda s: _IMPACT_ORDER.get(s.impact, 99))
    elif sort_key == "frequency":
        all_schedules.sort(key=lambda s: s.frequency.days)
    else:
        # Default: status order, with within-group ordering
        def _status_sort_key(s: Schedule) -> tuple[int, int]:
            st = s.schedule_status
            order = _STATUS_ORDER.get(st.status, 4)
            if st.status == "overdue":
                secondary = -(st.days_overdue or 0)  # most overdue first
            elif st.status == "due_soon":
                secondary = st.days_until_due or 0   # soonest first
            else:
                secondary = _PRIORITY_ORDER.get(s.priority, 2)
            return (order, secondary)
        all_schedules.sort(key=_status_sort_key)

    # Filter options
    categories = Category.objects.values_list("name", flat=True)
    frequencies = Frequency.objects.filter(schedules__active=True).distinct().order_by("days")

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
        "schedules": all_schedules,
        "projects": active_projects,
        "total_active": total_active,
        "today": today,
        "categories": categories,
        "frequencies": frequencies,
        "impact_choices": Schedule.IMPACT_CHOICES,
        "filters": {
            "priority": priority_filter,
            "category": category_filter,
            "impact": impact_filter,
            "frequency": frequency_filter,
            "show": show,
            "sort": sort,
        },
    }

    return render(request, "dashboard.html", context)

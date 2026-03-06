from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import WorkLog


@login_required
def spending_summary(request: HttpRequest) -> HttpResponse:
    now = timezone.now()
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Time periods
    periods = {
        "last_30": now - timedelta(days=30),
        "last_90": now - timedelta(days=90),
        "ytd": year_start,
        "all_time": None,
    }

    stats = {}
    for label, start in periods.items():
        qs = WorkLog.objects.all()
        if start:
            qs = qs.filter(completed_at__gte=start)

        agg = qs.aggregate(
            total_cost=Sum("cost"),
            total_entries=Count("id"),
            total_minutes=Sum("duration_minutes"),
        )
        stats[label] = {
            "total_cost": agg["total_cost"] or 0,
            "total_entries": agg["total_entries"] or 0,
            "total_minutes": agg["total_minutes"] or 0,
        }

    # Category breakdown (YTD) — only entries with actual cost
    category_qs = (
        WorkLog.objects.filter(completed_at__gte=year_start, cost__gt=0)
        .values("schedule__category")
        .annotate(total=Sum("cost"), count=Count("id"))
        .order_by("-total")
    )
    categories = [
        {"name": row["schedule__category"] or "Uncategorized", "total": row["total"] or 0, "count": row["count"]}
        for row in category_qs
    ]

    # Recent work logs with cost only
    recent_logs = (
        WorkLog.objects.filter(cost__gt=0)
        .select_related("schedule", "project", "asset")
        .order_by("-completed_at")[:25]
    )

    # Monthly spending (last 12 months)
    months = []
    for i in range(11, -1, -1):
        # Proper month arithmetic to avoid timedelta drift
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        month_start = now.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            month_end = now.replace(year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now

        agg = WorkLog.objects.filter(
            completed_at__gte=month_start,
            completed_at__lt=month_end,
            cost__gt=0,
        ).aggregate(total=Sum("cost"), count=Count("id"))

        months.append({
            "label": month_start.strftime("%b %Y"),
            "total": agg["total"] or 0,
            "count": agg["count"] or 0,
        })

    context = {
        "stats": stats,
        "categories": categories,
        "recent_logs": recent_logs,
        "months": months,
        "has_any_costs": WorkLog.objects.filter(cost__gt=0).exists(),
    }
    return render(request, "spending/summary.html", context)

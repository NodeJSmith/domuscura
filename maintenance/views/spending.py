from datetime import timedelta

from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.utils import timezone

from maintenance.models import WorkLog


def spending_summary(request):
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

    # Category breakdown (YTD) via schedule or project category
    category_qs = (
        WorkLog.objects.filter(completed_at__gte=year_start)
        .values("schedule__category")
        .annotate(total=Sum("cost"), count=Count("id"))
        .order_by("-total")
    )
    categories = [
        {"name": row["schedule__category"] or "Uncategorized", "total": row["total"] or 0, "count": row["count"]}
        for row in category_qs
    ]

    # Recent work logs
    recent_logs = (
        WorkLog.objects.select_related("schedule", "project", "asset")
        .order_by("-completed_at")[:25]
    )

    # Monthly spending (last 12 months)
    months = []
    for i in range(11, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        if i > 0:
            month_end = (now.replace(day=1) - timedelta(days=30 * (i - 1))).replace(day=1)
        else:
            month_end = now

        agg = WorkLog.objects.filter(
            completed_at__gte=month_start,
            completed_at__lt=month_end,
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
    }
    return render(request, "spending/summary.html", context)

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from maintenance.models import (
    Asset,
    Issue,
    Location,
    Project,
    Schedule,
    WorkLog,
)


@pytest.fixture
def base_url(live_server):
    """Override Playwright's base_url to point at the Django live server."""
    return live_server.url


@pytest.fixture
def seeded_db(db):
    """Create a minimal set of test data for e2e tests."""
    loc = Location.objects.create(name="Basement", notes="Lower level")
    loc2 = Location.objects.create(name="Kitchen", notes="Main floor")

    asset = Asset.objects.create(
        name="Central AC",
        location=loc,
        category="HVAC",
        make="Carrier",
    )

    # Never-done schedule
    sched = Schedule.objects.create(
        name="Replace HVAC Filter",
        asset=asset,
        location=loc,
        category="HVAC",
        frequency_days=90,
        priority="high",
        impact="efficiency",
        active=True,
    )

    # Overdue schedule
    overdue = Schedule.objects.create(
        name="Clean Gutters",
        location=loc,
        category="Exterior",
        frequency_days=180,
        priority="critical",
        impact="protective",
        active=True,
    )
    WorkLog.objects.create(
        schedule=overdue,
        completed_at=timezone.now() - timedelta(days=200),
        performed_by="self",
    )

    project = Project.objects.create(
        name="Replace Roof",
        location=loc,
        priority="high",
        status="pending",
        target_date=timezone.now().date() + timedelta(days=30),
        estimated_cost=Decimal("15000.00"),
    )

    issue = Issue.objects.create(
        summary="Cracked foundation",
        location=loc,
        severity="major",
        status="open",
    )

    return {
        "location": loc,
        "asset": asset,
        "schedule": sched,
        "overdue_schedule": overdue,
        "project": project,
        "issue": issue,
    }

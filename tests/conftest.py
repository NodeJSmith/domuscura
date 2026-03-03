from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from maintenance.models import (
    Asset,
    Document,
    Issue,
    Location,
    Project,
    Schedule,
    WorkLog,
)


@pytest.fixture
def location(db):
    return Location.objects.create(name="Basement", notes="Lower level")


@pytest.fixture
def location2(db):
    return Location.objects.create(name="Kitchen", notes="Main floor kitchen")


@pytest.fixture
def asset(db, location):
    return Asset.objects.create(
        name="Central AC",
        location=location,
        category="HVAC",
        make="Carrier",
        model_name="24ACC636",
        serial_number="SN-12345",
        install_date=timezone.now().date() - timedelta(days=730),
        warranty_expires=timezone.now().date() + timedelta(days=365),
        expected_lifespan_years=15,
        purchase_price=Decimal("4500.00"),
    )


@pytest.fixture
def asset_expired_warranty(db, location):
    return Asset.objects.create(
        name="Old Furnace",
        location=location,
        category="HVAC",
        warranty_expires=timezone.now().date() - timedelta(days=30),
    )


@pytest.fixture
def asset_no_warranty(db, location):
    return Asset.objects.create(
        name="Sump Pump",
        location=location,
        category="Plumbing",
    )


@pytest.fixture
def schedule(db, asset, location):
    return Schedule.objects.create(
        name="Replace HVAC Filter",
        description="Swap out the air filter",
        asset=asset,
        location=location,
        category="HVAC",
        frequency_days=90,
        frequency_label="Quarterly",
        priority="high",
        impact="efficiency",
        estimated_minutes=15,
        estimated_cost=Decimal("25.00"),
        active=True,
    )


@pytest.fixture
def inactive_schedule(db, location):
    return Schedule.objects.create(
        name="Inactive Task",
        frequency_days=365,
        priority="low",
        active=False,
        location=location,
    )


@pytest.fixture
def schedule_with_log(db, schedule):
    """A schedule that was completed 10 days ago (status: ok for 90-day freq)."""
    WorkLog.objects.create(
        schedule=schedule,
        completed_at=timezone.now() - timedelta(days=10),
        performed_by="self",
    )
    return schedule


@pytest.fixture
def overdue_schedule(db, location):
    """A schedule that is overdue (completed 200 days ago, frequency 180)."""
    sched = Schedule.objects.create(
        name="Overdue Task",
        frequency_days=180,
        priority="critical",
        impact="safety",
        active=True,
        location=location,
    )
    WorkLog.objects.create(
        schedule=sched,
        completed_at=timezone.now() - timedelta(days=200),
        performed_by="self",
    )
    return sched


@pytest.fixture
def due_soon_schedule(db, location):
    """A schedule that is due soon (completed 80 days ago, frequency 90)."""
    sched = Schedule.objects.create(
        name="Due Soon Task",
        frequency_days=90,
        priority="normal",
        active=True,
        location=location,
    )
    WorkLog.objects.create(
        schedule=sched,
        completed_at=timezone.now() - timedelta(days=80),
        performed_by="self",
    )
    return sched


@pytest.fixture
def project(db, location):
    return Project.objects.create(
        name="Replace Roof",
        description="Full roof replacement",
        location=location,
        category="Exterior",
        priority="high",
        impact="protective",
        status="pending",
        target_date=timezone.now().date() + timedelta(days=30),
        estimated_cost=Decimal("15000.00"),
    )


@pytest.fixture
def someday_project(db):
    return Project.objects.create(
        name="Finish Basement",
        status="someday",
        priority="low",
    )


@pytest.fixture
def overdue_project(db):
    return Project.objects.create(
        name="Fix Deck",
        status="pending",
        priority="high",
        target_date=timezone.now().date() - timedelta(days=7),
    )


@pytest.fixture
def issue(db, location):
    return Issue.objects.create(
        summary="Cracked foundation wall",
        details="Hairline crack on east wall",
        location=location,
        severity="major",
        status="open",
        source="home_inspector",
        discovered_at=timezone.now().date() - timedelta(days=60),
    )


@pytest.fixture
def work_log(db, schedule):
    return WorkLog.objects.create(
        schedule=schedule,
        completed_at=timezone.now(),
        performed_by="self",
        cost=Decimal("25.00"),
        duration_minutes=20,
        notes="Replaced with MERV-13 filter",
    )

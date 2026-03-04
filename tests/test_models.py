from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError
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


class TestLocation:
    def test_str(self, location):
        assert str(location) == "Basement"

    def test_unique_name(self, location):
        with pytest.raises(IntegrityError):
            Location.objects.create(name="Basement")

    def test_ordering(self, location, location2):
        locs = list(Location.objects.values_list("name", flat=True))
        assert locs == ["Basement", "Kitchen"]

    def test_default_notes(self, db):
        loc = Location.objects.create(name="Attic")
        assert loc.notes == ""


class TestAsset:
    def test_str(self, asset):
        assert str(asset) == "Central AC"

    def test_warranty_status_active(self, asset):
        assert asset.warranty_status == "active"

    def test_warranty_status_expired(self, asset_expired_warranty):
        assert asset_expired_warranty.warranty_status == "expired"

    def test_warranty_status_unknown(self, asset_no_warranty):
        assert asset_no_warranty.warranty_status == "unknown"

    def test_age_years(self, asset):
        assert asset.age_years == 2

    def test_age_years_none(self, asset_no_warranty):
        assert asset_no_warranty.age_years is None

    def test_ordering(self, db, location):
        Asset.objects.create(name="Dishwasher", category="Appliance", location=location)
        Asset.objects.create(name="Fridge", category="Appliance", location=location)
        Asset.objects.create(name="Boiler", category="HVAC", location=location)
        assets = list(Asset.objects.values_list("category", "name"))
        # Ordered by category then name: Appliance < HVAC
        assert assets[0] == ("Appliance", "Dishwasher")
        assert assets[1] == ("Appliance", "Fridge")
        assert assets[2] == ("HVAC", "Boiler")

    def test_category_choices(self):
        categories = [c[0] for c in Asset.CATEGORY_CHOICES]
        assert "HVAC" in categories
        assert "Plumbing" in categories
        assert len(categories) == 8


class TestSchedule:
    def test_str(self, schedule):
        assert str(schedule) == "Replace HVAC Filter"

    def test_effective_category_from_schedule(self, schedule):
        assert schedule.effective_category == "HVAC"

    def test_effective_category_from_asset(self, db, asset):
        sched = Schedule.objects.create(
            name="Test", frequency_days=30, asset=asset, category=""
        )
        assert sched.effective_category == "HVAC"

    def test_effective_category_empty(self, db):
        sched = Schedule.objects.create(name="Test", frequency_days=30, category="")
        assert sched.effective_category == ""

    def test_effective_location_from_schedule(self, schedule, location):
        assert schedule.effective_location == location

    def test_effective_location_from_asset(self, db, asset, location):
        sched = Schedule.objects.create(
            name="Test", frequency_days=30, asset=asset, location=None
        )
        assert sched.effective_location == location

    def test_effective_location_none(self, db):
        sched = Schedule.objects.create(
            name="Test", frequency_days=30, asset=None, location=None
        )
        assert sched.effective_location is None

    def test_default_values(self, db):
        sched = Schedule.objects.create(name="Minimal", frequency_days=7)
        assert sched.priority == "normal"
        assert sched.active is True
        assert sched.pro_recommended is False


class TestProject:
    def test_str(self, project):
        assert str(project) == "Replace Roof"

    def test_effective_status_someday(self, someday_project):
        assert someday_project.effective_status == "someday"

    def test_effective_status_overdue(self, overdue_project):
        assert overdue_project.effective_status == "overdue"

    def test_effective_status_due_soon(self, db):
        p = Project.objects.create(
            name="Soon",
            status="pending",
            target_date=timezone.now().date() + timedelta(days=7),
        )
        assert p.effective_status == "due_soon"

    def test_effective_status_normal(self, project):
        # target_date is 30 days out, status is pending
        assert project.effective_status == "pending"

    def test_effective_status_no_target_date(self, db):
        p = Project.objects.create(name="No Date", status="in_progress")
        assert p.effective_status == "in_progress"

    def test_effective_status_done_with_past_target(self, db):
        p = Project.objects.create(
            name="Done",
            status="done",
            target_date=timezone.now().date() - timedelta(days=30),
        )
        assert p.effective_status == "done"

    def test_effective_status_cancelled_with_past_target(self, db):
        p = Project.objects.create(
            name="Cancelled",
            status="cancelled",
            target_date=timezone.now().date() - timedelta(days=30),
        )
        assert p.effective_status == "cancelled"


class TestIssue:
    def test_str(self, issue):
        assert str(issue) == "Cracked foundation wall"

    def test_ordering_by_severity(self, db, location):
        Issue.objects.create(summary="Cosmetic", severity="cosmetic", location=location)
        Issue.objects.create(summary="Safety", severity="safety", location=location)
        Issue.objects.create(summary="Minor", severity="minor", location=location)
        issues = list(Issue.objects.values_list("summary", flat=True))
        assert issues[0] == "Safety"
        assert issues[-1] == "Cosmetic"

    def test_default_values(self, db):
        i = Issue.objects.create(summary="Test issue")
        assert i.severity == "minor"
        assert i.status == "open"


class TestWorkLog:
    def test_str_with_schedule(self, work_log, schedule):
        assert "Replace HVAC Filter" in str(work_log)

    def test_str_with_project(self, db, project):
        wl = WorkLog.objects.create(
            project=project,
            completed_at=timezone.now(),
        )
        assert "Replace Roof" in str(wl)

    def test_str_adhoc(self, db):
        wl = WorkLog.objects.create(completed_at=timezone.now())
        assert "Ad-hoc" in str(wl)

    def test_constraint_both_schedule_and_project(self, db, schedule, project):
        with pytest.raises(IntegrityError):
            WorkLog.objects.create(
                schedule=schedule,
                project=project,
                completed_at=timezone.now(),
            )

    def test_ordering(self, db, schedule):
        wl1 = WorkLog.objects.create(
            schedule=schedule, completed_at=timezone.now() - timedelta(days=1)
        )
        wl2 = WorkLog.objects.create(
            schedule=schedule, completed_at=timezone.now()
        )
        logs = list(WorkLog.objects.all())
        assert logs[0].pk == wl2.pk  # most recent first


class TestDocument:
    def test_str(self, db):
        doc = Document.objects.create(filename="receipt.pdf", file="documents/receipt.pdf")
        assert str(doc) == "receipt.pdf"

    def test_relations(self, db, asset, work_log, issue, project):
        doc = Document.objects.create(
            filename="test.pdf",
            file="documents/test.pdf",
            asset=asset,
        )
        assert doc.asset == asset
        assert doc in asset.documents.all()

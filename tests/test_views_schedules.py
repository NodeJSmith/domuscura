import pytest
from django.test import Client
from django.urls import reverse

from maintenance.models import Location, Schedule, WorkLog


@pytest.fixture
def client():
    return Client()


class TestScheduleList:
    def test_list_loads(self, client, db):
        resp = client.get(reverse("schedule_list"))
        assert resp.status_code == 200

    def test_list_shows_active_by_default(self, client, schedule, inactive_schedule):
        resp = client.get(reverse("schedule_list"))
        names = [s.name for s in resp.context["schedules"]]
        assert schedule.name in names
        assert inactive_schedule.name not in names

    def test_list_filter_inactive(self, client, schedule, inactive_schedule):
        resp = client.get(reverse("schedule_list"), {"active": "inactive"})
        names = [s.name for s in resp.context["schedules"]]
        assert inactive_schedule.name in names
        assert schedule.name not in names

    def test_list_filter_all(self, client, schedule, inactive_schedule):
        resp = client.get(reverse("schedule_list"), {"active": "all"})
        names = [s.name for s in resp.context["schedules"]]
        assert schedule.name in names
        assert inactive_schedule.name in names

    def test_list_filter_by_category(self, client, schedule):
        resp = client.get(reverse("schedule_list"), {"category": "HVAC"})
        assert len(resp.context["schedules"]) == 1

        resp = client.get(reverse("schedule_list"), {"category": "Plumbing"})
        assert len(resp.context["schedules"]) == 0

    def test_list_filter_by_priority(self, client, schedule):
        resp = client.get(reverse("schedule_list"), {"priority": "high"})
        assert len(resp.context["schedules"]) == 1

        resp = client.get(reverse("schedule_list"), {"priority": "low"})
        assert len(resp.context["schedules"]) == 0

    def test_list_filter_by_search(self, client, schedule):
        resp = client.get(reverse("schedule_list"), {"q": "HVAC"})
        assert len(resp.context["schedules"]) == 1

        resp = client.get(reverse("schedule_list"), {"q": "nonexistent"})
        assert len(resp.context["schedules"]) == 0

    def test_list_filter_by_status(self, client, overdue_schedule, schedule):
        resp = client.get(reverse("schedule_list"), {"status": "overdue"})
        names = [s.name for s in resp.context["schedules"]]
        assert "Overdue Task" in names
        assert "Replace HVAC Filter" not in names

    def test_list_filter_by_location(self, client, schedule, location, location2):
        resp = client.get(reverse("schedule_list"), {"location": location.pk})
        assert len(resp.context["schedules"]) == 1

        resp = client.get(reverse("schedule_list"), {"location": location2.pk})
        assert len(resp.context["schedules"]) == 0

    def test_list_sort_by_name(self, client, db, location):
        Schedule.objects.create(name="Zebra Task", frequency_days=30, active=True, location=location)
        Schedule.objects.create(name="Alpha Task", frequency_days=30, active=True, location=location)
        resp = client.get(reverse("schedule_list"), {"sort": "name"})
        names = [s.name for s in resp.context["schedules"]]
        assert names == sorted(names, key=str.lower)

    def test_list_sort_reverse(self, client, db, location):
        Schedule.objects.create(name="Zebra Task", frequency_days=30, active=True, location=location)
        Schedule.objects.create(name="Alpha Task", frequency_days=30, active=True, location=location)
        resp = client.get(reverse("schedule_list"), {"sort": "-name"})
        names = [s.name for s in resp.context["schedules"]]
        assert names == sorted(names, key=str.lower, reverse=True)

    def test_list_htmx_returns_partial(self, client, schedule):
        resp = client.get(
            reverse("schedule_list"),
            HTTP_HX_REQUEST="true",
        )
        assert resp.status_code == 200
        # Should use partial template
        template_names = [t.name for t in resp.templates]
        assert "partials/schedule_list_body.html" in template_names


class TestScheduleDetail:
    def test_detail_loads(self, client, schedule):
        resp = client.get(reverse("schedule_detail", args=[schedule.pk]))
        assert resp.status_code == 200
        assert resp.context["schedule"].name == "Replace HVAC Filter"

    def test_detail_never_done_status(self, client, schedule):
        resp = client.get(reverse("schedule_detail", args=[schedule.pk]))
        assert resp.context["schedule"].status == "never_done"

    def test_detail_ok_status(self, client, schedule_with_log):
        resp = client.get(reverse("schedule_detail", args=[schedule_with_log.pk]))
        assert resp.context["schedule"].status == "ok"

    def test_detail_overdue_status(self, client, overdue_schedule):
        resp = client.get(reverse("schedule_detail", args=[overdue_schedule.pk]))
        assert resp.context["schedule"].status == "overdue"

    def test_detail_404(self, client, db):
        resp = client.get(reverse("schedule_detail", args=[99999]))
        assert resp.status_code == 404

    def test_detail_shows_work_logs(self, client, schedule_with_log):
        resp = client.get(reverse("schedule_detail", args=[schedule_with_log.pk]))
        assert len(resp.context["work_logs"]) == 1


class TestScheduleCreate:
    def test_create_get(self, client, db):
        resp = client.get(reverse("schedule_create"))
        assert resp.status_code == 200
        assert resp.context["editing"] is False

    def test_create_post_valid(self, client, db):
        resp = client.post(reverse("schedule_create"), {
            "name": "New Schedule",
            "frequency_days": 60,
            "priority": "normal",
            "active": True,
        })
        assert resp.status_code == 302
        sched = Schedule.objects.get(name="New Schedule")
        assert sched.frequency_days == 60

    def test_create_post_invalid(self, client, db):
        resp = client.post(reverse("schedule_create"), {"name": ""})
        assert resp.status_code == 200  # re-renders form


class TestScheduleEdit:
    def test_edit_get(self, client, schedule):
        resp = client.get(reverse("schedule_edit", args=[schedule.pk]))
        assert resp.status_code == 200
        assert resp.context["editing"] is True

    def test_edit_post_valid(self, client, schedule):
        resp = client.post(reverse("schedule_edit", args=[schedule.pk]), {
            "name": "Updated Name",
            "frequency_days": 60,
            "priority": "low",
            "active": True,
        })
        assert resp.status_code == 302
        schedule.refresh_from_db()
        assert schedule.name == "Updated Name"

    def test_edit_post_invalid(self, client, schedule):
        resp = client.post(reverse("schedule_edit", args=[schedule.pk]), {"name": ""})
        assert resp.status_code == 200

    def test_edit_404(self, client, db):
        resp = client.get(reverse("schedule_edit", args=[99999]))
        assert resp.status_code == 404


class TestScheduleToggleActive:
    def test_toggle_active_to_inactive(self, client, schedule):
        assert schedule.active is True
        resp = client.post(reverse("schedule_toggle_active", args=[schedule.pk]))
        assert resp.status_code == 302  # non-HTMX redirect
        schedule.refresh_from_db()
        assert schedule.active is False

    def test_toggle_inactive_to_active(self, client, inactive_schedule):
        resp = client.post(reverse("schedule_toggle_active", args=[inactive_schedule.pk]))
        inactive_schedule.refresh_from_db()
        assert inactive_schedule.active is True

    def test_toggle_htmx_returns_partial(self, client, schedule):
        resp = client.post(
            reverse("schedule_toggle_active", args=[schedule.pk]),
            HTTP_HX_REQUEST="true",
        )
        assert resp.status_code == 200
        assert "partials/schedule_row.html" in [t.name for t in resp.templates]

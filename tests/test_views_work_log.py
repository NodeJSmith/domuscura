import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from maintenance.models import Schedule, WorkLog


@pytest.fixture
def client():
    return Client()


class TestQuickLog:
    def test_quick_log_creates_work_log(self, client, schedule):
        assert WorkLog.objects.count() == 0
        resp = client.post(reverse("quick_log", args=[schedule.pk]))
        assert resp.status_code == 200
        assert WorkLog.objects.count() == 1
        wl = WorkLog.objects.first()
        assert wl.schedule == schedule
        assert wl.performed_by == "self"

    def test_quick_log_returns_card_partial(self, client, schedule):
        resp = client.post(reverse("quick_log", args=[schedule.pk]))
        assert resp.status_code == 200
        assert "partials/schedule_card.html" in [t.name for t in resp.templates]

    def test_quick_log_get_not_allowed(self, client, schedule):
        resp = client.get(reverse("quick_log", args=[schedule.pk]))
        assert resp.status_code == 405  # Method Not Allowed

    def test_quick_log_404(self, client, db):
        resp = client.post(reverse("quick_log", args=[99999]))
        assert resp.status_code == 404


class TestLogWorkForm:
    def test_form_get(self, client, db):
        resp = client.get(reverse("work_log_form"))
        assert resp.status_code == 200
        assert "form" in resp.context

    def test_form_get_with_schedule(self, client, schedule):
        resp = client.get(reverse("work_log_form_for_schedule", args=[schedule.pk]))
        assert resp.status_code == 200
        assert resp.context["schedule"] == schedule

    def test_form_post_with_schedule(self, client, schedule):
        resp = client.post(reverse("work_log_form"), {
            "schedule": schedule.pk,
            "performed_by": "self",
        })
        assert resp.status_code == 200
        assert WorkLog.objects.count() == 1
        # Should return schedule card partial
        assert "partials/schedule_card.html" in [t.name for t in resp.templates]

    def test_form_post_without_schedule(self, client, db):
        resp = client.post(reverse("work_log_form"), {
            "performed_by": "self",
        })
        assert resp.status_code == 200
        assert WorkLog.objects.count() == 1
        # Should return success message
        assert b"Work logged successfully" in resp.content

    def test_form_post_with_project(self, client, project):
        resp = client.post(reverse("work_log_form"), {
            "project": project.pk,
            "performed_by": "self",
        })
        assert resp.status_code == 200
        assert WorkLog.objects.count() == 1

    def test_form_post_invalid(self, client, schedule, project):
        resp = client.post(reverse("work_log_form"), {
            "schedule": schedule.pk,
            "project": project.pk,
        })
        assert resp.status_code == 200
        assert WorkLog.objects.count() == 0  # not saved

    def test_form_get_schedule_404(self, client, db):
        resp = client.get(reverse("work_log_form_for_schedule", args=[99999]))
        assert resp.status_code == 404

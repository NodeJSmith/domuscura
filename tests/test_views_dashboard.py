from django.urls import reverse


class TestDashboard:
    def test_dashboard_loads(self, client, db):
        resp = client.get(reverse("dashboard"))
        assert resp.status_code == 200

    def test_dashboard_empty_state(self, client, db):
        resp = client.get(reverse("dashboard"))
        assert resp.status_code == 200
        assert resp.context["total_active"] == 0

    def test_dashboard_shows_never_done(self, client, schedule):
        resp = client.get(reverse("dashboard"))
        assert len(resp.context["never_done"]) == 1
        assert resp.context["never_done"][0].name == "Replace HVAC Filter"

    def test_dashboard_shows_overdue(self, client, overdue_schedule):
        resp = client.get(reverse("dashboard"))
        assert len(resp.context["overdue"]) == 1
        assert resp.context["overdue"][0].schedule_status.status == "overdue"

    def test_dashboard_shows_due_soon(self, client, due_soon_schedule):
        resp = client.get(reverse("dashboard"))
        assert len(resp.context["due_soon"]) == 1
        assert resp.context["due_soon"][0].schedule_status.status == "due_soon"

    def test_dashboard_shows_ok(self, client, schedule_with_log):
        resp = client.get(reverse("dashboard"))
        assert len(resp.context["ok"]) == 1
        assert resp.context["ok"][0].schedule_status.status == "ok"

    def test_dashboard_excludes_inactive(self, client, inactive_schedule):
        resp = client.get(reverse("dashboard"))
        assert resp.context["total_active"] == 0

    def test_dashboard_total_active_count(
        self, client, schedule, overdue_schedule, due_soon_schedule, schedule_with_log
    ):
        # schedule = never_done, overdue, due_soon, schedule_with_log (ok)
        # But schedule_with_log uses the same schedule fixture, so it makes
        # that schedule "ok" instead of "never_done"
        resp = client.get(reverse("dashboard"))
        assert resp.context["total_active"] == 3  # overdue, due_soon, schedule(ok)

    def test_dashboard_overdue_sorted_by_most_overdue(self, client, db, location):
        from datetime import timedelta

        from django.utils import timezone

        from maintenance.models import Schedule, WorkLog

        s1 = Schedule.objects.create(
            name="S1", frequency_days=30, active=True, location=location
        )
        s2 = Schedule.objects.create(
            name="S2", frequency_days=30, active=True, location=location
        )
        WorkLog.objects.create(
            schedule=s1, completed_at=timezone.now() - timedelta(days=50), performed_by="self"
        )
        WorkLog.objects.create(
            schedule=s2, completed_at=timezone.now() - timedelta(days=100), performed_by="self"
        )
        resp = client.get(reverse("dashboard"))
        overdue = resp.context["overdue"]
        assert len(overdue) == 2
        assert overdue[0].name == "S2"  # more overdue comes first

    def test_dashboard_projects_excludes_done(self, client, project, db):
        from maintenance.models import Project

        Project.objects.create(name="Done Project", status="done")
        resp = client.get(reverse("dashboard"))
        project_names = [p.name for p in resp.context["projects"]]
        assert "Done Project" not in project_names
        assert "Replace Roof" in project_names

    def test_dashboard_project_effective_status(self, client, overdue_project):
        resp = client.get(reverse("dashboard"))
        projects = resp.context["projects"]
        assert len(projects) >= 1
        p = [p for p in projects if p.name == "Fix Deck"][0]
        assert p.effective_status_display == "overdue"

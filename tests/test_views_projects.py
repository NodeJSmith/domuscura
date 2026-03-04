from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from maintenance.models import Project


class TestProjectList:
    def test_list_loads(self, client, db):
        resp = client.get(reverse("project_list"))
        assert resp.status_code == 200

    def test_list_shows_projects(self, client, project):
        resp = client.get(reverse("project_list"))
        names = [p.name for p in resp.context["projects"]]
        assert "Replace Roof" in names

    def test_list_filter_by_status(self, client, project, someday_project):
        resp = client.get(reverse("project_list"), {"status": "someday"})
        names = [p.name for p in resp.context["projects"]]
        assert "Finish Basement" in names
        assert "Replace Roof" not in names

    def test_list_filter_by_priority(self, client, project, someday_project):
        resp = client.get(reverse("project_list"), {"priority": "high"})
        names = [p.name for p in resp.context["projects"]]
        assert "Replace Roof" in names
        assert "Finish Basement" not in names

    def test_list_filter_by_search(self, client, project):
        resp = client.get(reverse("project_list"), {"q": "Roof"})
        assert len(resp.context["projects"]) == 1

        resp = client.get(reverse("project_list"), {"q": "nonexistent"})
        assert len(resp.context["projects"]) == 0

    def test_list_effective_status_overdue(self, client, overdue_project):
        resp = client.get(reverse("project_list"))
        p = [p for p in resp.context["projects"] if p.name == "Fix Deck"][0]
        assert p.effective_status_display == "overdue"

    def test_list_effective_status_done(self, client, db):
        Project.objects.create(name="Done", status="done")
        resp = client.get(reverse("project_list"))
        p = [p for p in resp.context["projects"] if p.name == "Done"][0]
        assert p.effective_status_display == "done"

    def test_list_effective_status_due_soon(self, client, db):
        Project.objects.create(
            name="Soon",
            status="pending",
            target_date=timezone.now().date() + timedelta(days=7),
        )
        resp = client.get(reverse("project_list"))
        p = [p for p in resp.context["projects"] if p.name == "Soon"][0]
        assert p.effective_status_display == "due_soon"


class TestProjectDetail:
    def test_detail_loads(self, client, project):
        resp = client.get(reverse("project_detail", args=[project.pk]))
        assert resp.status_code == 200
        assert resp.context["project"].name == "Replace Roof"

    def test_detail_effective_status(self, client, overdue_project):
        resp = client.get(reverse("project_detail", args=[overdue_project.pk]))
        assert resp.context["project"].effective_status_display == "overdue"

    def test_detail_shows_work_logs(self, client, project, db):
        from maintenance.models import WorkLog

        WorkLog.objects.create(
            project=project, completed_at=timezone.now(), performed_by="self"
        )
        resp = client.get(reverse("project_detail", args=[project.pk]))
        assert len(resp.context["work_logs"]) == 1

    def test_detail_shows_issues(self, client, project, db):
        from maintenance.models import Issue

        Issue.objects.create(summary="Related Issue", project=project)
        resp = client.get(reverse("project_detail", args=[project.pk]))
        assert len(resp.context["issues"]) == 1

    def test_detail_404(self, client, db):
        resp = client.get(reverse("project_detail", args=[99999]))
        assert resp.status_code == 404


class TestProjectCreate:
    def test_create_get(self, client, db):
        resp = client.get(reverse("project_create"))
        assert resp.status_code == 200
        assert resp.context["editing"] is False

    def test_create_post_valid(self, client, db):
        resp = client.post(reverse("project_create"), {
            "name": "New Project",
            "priority": "normal",
            "status": "pending",
        })
        assert resp.status_code == 302
        assert Project.objects.filter(name="New Project").exists()

    def test_create_post_invalid(self, client, db):
        resp = client.post(reverse("project_create"), {"name": ""})
        assert resp.status_code == 200


class TestProjectEdit:
    def test_edit_get(self, client, project):
        resp = client.get(reverse("project_edit", args=[project.pk]))
        assert resp.status_code == 200
        assert resp.context["editing"] is True

    def test_edit_post_valid(self, client, project):
        resp = client.post(reverse("project_edit", args=[project.pk]), {
            "name": "Updated Project",
            "priority": "critical",
            "status": "in_progress",
        })
        assert resp.status_code == 302
        project.refresh_from_db()
        assert project.name == "Updated Project"
        assert project.status == "in_progress"

    def test_edit_404(self, client, db):
        resp = client.get(reverse("project_edit", args=[99999]))
        assert resp.status_code == 404


from django import forms
from django.utils import timezone

from maintenance.forms import (
    AssetForm,
    IssueForm,
    ProjectForm,
    ScheduleForm,
    WorkLogForm,
)


class TestAssetForm:
    def test_valid_minimal(self, db):
        form = AssetForm(data={"name": "Test Asset"})
        assert form.is_valid()

    def test_name_required(self, db):
        form = AssetForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_optional_fields(self, db):
        form = AssetForm(data={"name": "Test"})
        assert form.is_valid()
        # All other fields should be optional
        for field_name, field in form.fields.items():
            if field_name != "name":
                assert not field.required, f"{field_name} should be optional"

    def test_date_widgets(self):
        form = AssetForm()
        assert isinstance(form.fields["install_date"].widget, forms.DateInput)
        assert isinstance(form.fields["warranty_expires"].widget, forms.DateInput)


class TestProjectForm:
    def test_valid_minimal(self, db):
        form = ProjectForm(data={"name": "Test Project", "priority": "normal", "status": "pending"})
        assert form.is_valid()

    def test_name_required(self, db):
        form = ProjectForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_all_fields_present(self):
        form = ProjectForm()
        expected_fields = [
            "name", "description", "asset", "location", "category",
            "priority", "impact", "status", "target_date",
            "estimated_cost", "pro_recommended", "notes",
        ]
        for field in expected_fields:
            assert field in form.fields


class TestIssueForm:
    def test_valid_minimal(self, db):
        form = IssueForm(data={"summary": "Test Issue", "severity": "minor", "status": "open"})
        assert form.is_valid()

    def test_summary_required(self, db):
        form = IssueForm(data={})
        assert not form.is_valid()
        assert "summary" in form.errors

    def test_optional_fields(self):
        form = IssueForm()
        required_fields = {"summary", "severity", "status"}
        for field_name, field in form.fields.items():
            if field_name not in required_fields:
                assert not field.required, f"{field_name} should be optional"


class TestScheduleForm:
    def test_valid_minimal(self, db):
        form = ScheduleForm(data={"name": "Test Schedule", "frequency_days": 30, "priority": "normal"})
        assert form.is_valid()

    def test_name_and_frequency_required(self, db):
        form = ScheduleForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors
        assert "frequency_days" in form.errors

    def test_saves_correctly(self, db):
        form = ScheduleForm(data={
            "name": "Monthly Check",
            "frequency_days": 30,
            "priority": "high",
            "active": True,
        })
        assert form.is_valid()
        sched = form.save()
        assert sched.pk is not None
        assert sched.name == "Monthly Check"
        assert sched.frequency_days == 30


class TestWorkLogForm:
    def test_valid_minimal(self, db):
        form = WorkLogForm(data={})
        assert form.is_valid()

    def test_performed_by_default(self):
        form = WorkLogForm()
        assert form.fields["performed_by"].initial == "self"

    def test_clean_completed_at_defaults_to_now(self, db):
        form = WorkLogForm(data={})
        assert form.is_valid()
        wl = form.save()
        assert wl.completed_at is not None
        # Should be within last minute
        assert (timezone.now() - wl.completed_at).seconds < 60

    def test_clean_completed_at_preserves_value(self, db):
        dt = timezone.now() - timezone.timedelta(days=1)
        form = WorkLogForm(data={"completed_at": dt.strftime("%Y-%m-%dT%H:%M")})
        assert form.is_valid()
        wl = form.save()
        assert wl.completed_at.date() == dt.date()

    def test_clean_rejects_both_schedule_and_project(self, db, schedule, project):
        form = WorkLogForm(data={
            "schedule": schedule.pk,
            "project": project.pk,
        })
        assert not form.is_valid()
        assert "__all__" in form.errors or form.non_field_errors()

    def test_valid_with_schedule_only(self, db, schedule):
        form = WorkLogForm(data={"schedule": schedule.pk})
        assert form.is_valid()

    def test_valid_with_project_only(self, db, project):
        form = WorkLogForm(data={"project": project.pk})
        assert form.is_valid()

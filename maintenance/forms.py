from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django import forms
from django.utils import timezone

from .models import Asset, Category, Frequency, Issue, Location, Project, Schedule, WorkLog


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "location",
            "category",
            "make",
            "model_name",
            "serial_number",
            "install_date",
            "warranty_expires",
            "expected_lifespan_years",
            "purchase_price",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "install_date": forms.DateInput(attrs={"type": "date"}),
            "warranty_expires": forms.DateInput(attrs={"type": "date"}),
            "purchase_price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "expected_lifespan_years": forms.NumberInput(attrs={"min": "0"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["location"].required = False
        self.fields["category"].required = False
        self.fields["make"].required = False
        self.fields["model_name"].required = False
        self.fields["serial_number"].required = False
        self.fields["install_date"].required = False
        self.fields["warranty_expires"].required = False
        self.fields["expected_lifespan_years"].required = False
        self.fields["purchase_price"].required = False
        self.fields["notes"].required = False
        self.fields["location"].empty_label = "Unspecified"
        self.fields["category"].empty_label = "Uncategorized"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "asset",
            "location",
            "category",
            "priority",
            "impact",
            "status",
            "target_date",
            "estimated_cost",
            "pro_recommended",
            "notes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "estimated_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["asset"].required = False
        self.fields["location"].required = False
        self.fields["category"].required = False
        self.fields["impact"].required = False
        self.fields["target_date"].required = False
        self.fields["estimated_cost"].required = False
        self.fields["notes"].required = False
        self.fields["asset"].empty_label = "No specific asset"
        self.fields["location"].empty_label = "Unspecified"
        self.fields["category"].empty_label = "Uncategorized"
        self.fields["impact"].empty_label = "Unspecified"


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "summary",
            "details",
            "asset",
            "location",
            "severity",
            "status",
            "source",
            "discovered_at",
            "project",
            "notes",
        ]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "discovered_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["details"].required = False
        self.fields["asset"].required = False
        self.fields["location"].required = False
        self.fields["source"].required = False
        self.fields["discovered_at"].required = False
        self.fields["project"].required = False
        self.fields["notes"].required = False
        self.fields["asset"].empty_label = "No specific asset"
        self.fields["location"].empty_label = "Unspecified"
        self.fields["source"].empty_label = "Not recorded"
        self.fields["project"].empty_label = "No linked project"
        if not self.instance.pk:
            self.fields["discovered_at"].initial = date.today()


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class FrequencyForm(forms.ModelForm):
    class Meta:
        model = Frequency
        fields = ["label", "days"]
        widgets = {
            "days": forms.NumberInput(attrs={"min": "1"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            "name",
            "description",
            "asset",
            "location",
            "category",
            "frequency",
            "priority",
            "impact",
            "estimated_minutes",
            "estimated_cost",
            "pro_recommended",
            "active",
            "notes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "estimated_cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "estimated_minutes": forms.NumberInput(attrs={"min": "0"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["asset"].required = False
        self.fields["location"].required = False
        self.fields["category"].required = False
        self.fields["impact"].required = False
        self.fields["estimated_minutes"].required = False
        self.fields["estimated_cost"].required = False
        self.fields["notes"].required = False
        self.fields["asset"].empty_label = "No specific asset"
        self.fields["location"].empty_label = "Unspecified"
        self.fields["category"].empty_label = "Uncategorized"
        self.fields["impact"].empty_label = "Unspecified"


class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = [
            "schedule",
            "project",
            "asset",
            "completed_at",
            "performed_by",
            "cost",
            "duration_minutes",
            "notes",
        ]
        widgets = {
            "completed_at": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "0"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Make most fields optional in the form
        self.fields["schedule"].required = False
        self.fields["project"].required = False
        self.fields["asset"].required = False
        self.fields["completed_at"].required = False
        self.fields["performed_by"].initial = "self"
        self.fields["cost"].required = False
        self.fields["duration_minutes"].required = False
        self.fields["notes"].required = False
        self.fields["schedule"].empty_label = "No linked schedule"
        self.fields["project"].empty_label = "No linked project"
        self.fields["asset"].empty_label = "No specific asset"

    def clean_completed_at(self) -> datetime:
        val = self.cleaned_data.get("completed_at")
        if not val:
            return timezone.now()
        if isinstance(val, date) and not isinstance(val, datetime):
            return timezone.make_aware(datetime.combine(val, datetime.min.time()))
        return val

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        schedule = cleaned.get("schedule")
        project = cleaned.get("project")
        if schedule and project:
            raise forms.ValidationError(
                "A work log entry cannot be linked to both a schedule and a project."
            )
        return cleaned

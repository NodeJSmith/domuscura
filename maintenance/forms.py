from django import forms
from django.utils import timezone

from .models import WorkLog


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
            "completed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "cost": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "0"}),
        }

    def __init__(self, *args, **kwargs):
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

    def clean_completed_at(self):
        val = self.cleaned_data.get("completed_at")
        if not val:
            return timezone.now()
        return val

    def clean(self):
        cleaned = super().clean()
        schedule = cleaned.get("schedule")
        project = cleaned.get("project")
        if schedule and project:
            raise forms.ValidationError(
                "A work log entry cannot be linked to both a schedule and a project."
            )
        return cleaned

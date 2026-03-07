from __future__ import annotations

from datetime import date, datetime
from typing import NamedTuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Asset(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    make = models.CharField(max_length=200, blank=True, default="")
    model_name = models.CharField(
        max_length=200, blank=True, default="", db_column="model"
    )
    serial_number = models.CharField(max_length=200, blank=True, default="")
    install_date = models.DateField(null=True, blank=True)
    warranty_expires = models.DateField(null=True, blank=True)
    expected_lifespan_years = models.PositiveIntegerField(null=True, blank=True)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self) -> str:
        return self.name

    @property
    def warranty_status(self) -> str:
        if not self.warranty_expires:
            return "unknown"
        if self.warranty_expires < timezone.now().date():
            return "expired"
        return "active"

    @property
    def age_years(self) -> int | None:
        if not self.install_date:
            return None
        delta = timezone.now().date() - self.install_date
        return delta.days // 365


class Frequency(models.Model):
    days = models.PositiveIntegerField()
    label = models.CharField(max_length=100)

    class Meta:
        ordering = ["days"]
        verbose_name_plural = "frequencies"

    def __str__(self) -> str:
        return self.label or f"Every {self.days} day{'s' if self.days != 1 else ''}"


class ScheduleStatus(NamedTuple):
    """Immutable computed status for a Schedule. Returned by Schedule.compute_status()."""

    status: str  # "never_done" | "overdue" | "due_soon" | "ok"
    last_completed: datetime | None
    days_since_last: int | None
    next_due_date: date | None
    days_overdue: int | None  # set only when status == "overdue"
    days_until_due: int | None  # set when status in ("due_soon", "ok")


class Schedule(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    IMPACT_CHOICES = [
        ("safety", "Safety"),
        ("protective", "Protective"),
        ("efficiency", "Efficiency"),
        ("cosmetic", "Cosmetic"),
        ("comfort", "Comfort"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name="schedules"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    frequency = models.ForeignKey(
        "Frequency", on_delete=models.PROTECT, related_name="schedules"
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="normal")
    impact = models.CharField(
        max_length=20, choices=IMPACT_CHOICES, blank=True, default=""
    )
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    pro_recommended = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def effective_category(self) -> str:
        if self.category:
            return self.category.name
        if self.asset and self.asset.category:
            return self.asset.category.name
        return ""

    @property
    def effective_location(self) -> Location | None:
        if self.location:
            return self.location
        if self.asset and self.asset.location:
            return self.asset.location
        return None

    @classmethod
    def annotate_last_completed(cls, queryset: QuerySet[Schedule]) -> QuerySet[Schedule]:
        """Annotate a Schedule queryset with last_completed from WorkLog."""
        from django.db.models import OuterRef, Subquery

        last_completion = (
            WorkLog.objects.filter(schedule=OuterRef("pk"))
            .order_by("-completed_at")
            .values("completed_at")[:1]
        )
        return queryset.annotate(last_completed=Subquery(last_completion))

    def compute_status(
        self, last_completed: datetime | None, now: datetime | None = None
    ) -> ScheduleStatus:
        """Return a ScheduleStatus for this schedule. Pure — no side effects on self."""
        from datetime import timedelta

        if now is None:
            now = timezone.now()

        if last_completed is None:
            return ScheduleStatus(
                status="never_done",
                last_completed=None,
                days_since_last=None,
                next_due_date=None,
                days_overdue=None,
                days_until_due=None,
            )

        days_since = (now - last_completed).days
        next_due_date = (last_completed + timedelta(days=self.frequency.days)).date()

        if days_since > self.frequency.days:
            return ScheduleStatus(
                status="overdue",
                last_completed=last_completed,
                days_since_last=days_since,
                next_due_date=next_due_date,
                days_overdue=days_since - self.frequency.days,
                days_until_due=None,
            )
        elif days_since > self.frequency.days * 0.85:
            return ScheduleStatus(
                status="due_soon",
                last_completed=last_completed,
                days_since_last=days_since,
                next_due_date=next_due_date,
                days_overdue=None,
                days_until_due=self.frequency.days - days_since,
            )
        else:
            return ScheduleStatus(
                status="ok",
                last_completed=last_completed,
                days_since_last=days_since,
                next_due_date=next_due_date,
                days_overdue=None,
                days_until_due=self.frequency.days - days_since,
            )


class Project(models.Model):
    PRIORITY_CHOICES = Schedule.PRIORITY_CHOICES
    IMPACT_CHOICES = Schedule.IMPACT_CHOICES
    STATUS_CHOICES = [
        ("someday", "Someday"),
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="normal")
    impact = models.CharField(
        max_length=20, choices=IMPACT_CHOICES, blank=True, default=""
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    target_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    pro_recommended = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "target_date"]

    def __str__(self) -> str:
        return self.name

    @property
    def effective_status(self) -> str:
        if self.status in ("done", "cancelled"):
            return self.status
        if self.status == "someday":
            return "someday"
        if self.target_date:
            today = timezone.now().date()
            if self.target_date < today:
                return "overdue"
            if (self.target_date - today).days <= 14:
                return "due_soon"
        return self.status


class Issue(models.Model):
    SEVERITY_CHOICES = [
        ("cosmetic", "Cosmetic"),
        ("minor", "Minor"),
        ("moderate", "Moderate"),
        ("major", "Major"),
        ("safety", "Safety"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("monitoring", "Monitoring"),
        ("accepted", "Accepted"),
        ("scheduled", "Scheduled"),
        ("resolved", "Resolved"),
    ]
    SOURCE_CHOICES = [
        ("self", "Self"),
        ("home_inspector", "Home Inspector"),
        ("contractor", "Contractor"),
    ]

    summary = models.CharField(max_length=300)
    details = models.TextField(blank=True, default="")
    asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name="issues"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, default="minor"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, blank=True, default=""
    )
    discovered_at = models.DateField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="issues"
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(severity="safety", then=0),
                models.When(severity="major", then=1),
                models.When(severity="moderate", then=2),
                models.When(severity="minor", then=3),
                models.When(severity="cosmetic", then=4),
                default=5,
                output_field=models.IntegerField(),
            ),
            "discovered_at",
        ]

    def __str__(self) -> str:
        return self.summary


class WorkLog(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_logs",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_logs",
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_logs",
    )
    completed_at = models.DateTimeField()
    performed_by = models.CharField(max_length=200, blank=True, default="")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        constraints = [
            models.CheckConstraint(
                condition=~(
                    models.Q(schedule__isnull=False) & models.Q(project__isnull=False)
                ),
                name="worklog_not_both_schedule_and_project",
            ),
        ]

    def __str__(self) -> str:
        source = self.schedule or self.project or "Ad-hoc"
        return f"{source} — {self.completed_at:%Y-%m-%d}"


class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ("receipt", "Receipt"),
        ("warranty", "Warranty"),
        ("manual", "Manual"),
        ("photo", "Photo"),
        ("invoice", "Invoice"),
        ("estimate", "Estimate"),
        ("other", "Other"),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    work_log = models.ForeignKey(
        WorkLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/%Y/%m/")
    doc_type = models.CharField(
        max_length=20, choices=DOC_TYPE_CHOICES, blank=True, default=""
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.filename

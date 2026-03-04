from django.db import models
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Asset(models.Model):
    CATEGORY_CHOICES = [
        ("HVAC", "HVAC"),
        ("Plumbing", "Plumbing"),
        ("Electrical", "Electrical"),
        ("Exterior", "Exterior"),
        ("Interior", "Interior"),
        ("Appliance", "Appliance"),
        ("Safety", "Safety"),
        ("Structural", "Structural"),
    ]

    name = models.CharField(max_length=200)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.CharField(max_length=50, blank=True, default="")
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
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    @property
    def warranty_status(self):
        if not self.warranty_expires:
            return "unknown"
        if self.warranty_expires < timezone.now().date():
            return "expired"
        return "active"

    @property
    def age_years(self):
        if not self.install_date:
            return None
        delta = timezone.now().date() - self.install_date
        return delta.days // 365


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
    category = models.CharField(max_length=50, blank=True, default="")
    frequency_days = models.PositiveIntegerField()
    frequency_label = models.CharField(max_length=50, blank=True, default="")
    season_hint = models.CharField(max_length=50, blank=True, default="")
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

    def __str__(self):
        return self.name

    @property
    def effective_category(self):
        if self.category:
            return self.category
        if self.asset:
            return self.asset.category
        return ""

    @property
    def effective_location(self):
        if self.location:
            return self.location
        if self.asset and self.asset.location:
            return self.asset.location
        return None

    @classmethod
    def annotate_last_completed(cls, queryset):
        """Annotate a Schedule queryset with last_completed from WorkLog."""
        from django.db.models import OuterRef, Subquery

        last_completion = (
            WorkLog.objects.filter(schedule=OuterRef("pk"))
            .order_by("-completed_at")
            .values("completed_at")[:1]
        )
        return queryset.annotate(last_completed=Subquery(last_completion))

    def compute_status(self, last_completed, now=None):
        """Compute and set status attributes based on last completion time.

        Sets: status, days_since_last, next_due_date, and either
        days_overdue or days_until_due on self.
        """
        from datetime import timedelta

        if now is None:
            now = timezone.now()

        self.last_completed = last_completed

        if last_completed is None:
            self.status = "never_done"
            self.days_since_last = None
            self.next_due_date = None
        else:
            days_since = (now - last_completed).days
            self.days_since_last = days_since
            self.next_due_date = (last_completed + timedelta(days=self.frequency_days)).date()
            if days_since > self.frequency_days:
                self.status = "overdue"
                self.days_overdue = days_since - self.frequency_days
            elif days_since > self.frequency_days * 0.85:
                self.status = "due_soon"
                self.days_until_due = self.frequency_days - days_since
            else:
                self.status = "ok"
                self.days_until_due = self.frequency_days - days_since


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
    category = models.CharField(max_length=50, blank=True, default="")
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

    def __str__(self):
        return self.name

    @property
    def effective_status(self):
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

    def __str__(self):
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

    def __str__(self):
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

    def __str__(self):
        return self.filename

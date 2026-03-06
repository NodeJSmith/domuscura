from django.contrib import admin

from .models import Asset, Document, Frequency, Issue, Location, Project, Schedule, WorkLog


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "notes"]
    search_fields = ["name"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "location",
        "make",
        "model_name",
        "install_date",
        "warranty_status",
    ]
    list_filter = ["category", "location"]
    search_fields = ["name", "make", "model_name", "serial_number"]

    @admin.display(description="Warranty")
    def warranty_status(self, obj):
        return obj.warranty_status


@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ["label", "days"]
    ordering = ["days"]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "frequency",
        "priority",
        "impact",
        "active",
        "pro_recommended",
    ]
    list_filter = ["category", "priority", "impact", "active", "pro_recommended", "frequency"]
    search_fields = ["name", "description"]
    list_editable = ["active"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "priority",
        "impact",
        "status",
        "target_date",
    ]
    list_filter = ["status", "priority", "impact", "category"]
    search_fields = ["name", "description"]


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = [
        "summary",
        "severity",
        "status",
        "source",
        "asset",
        "discovered_at",
    ]
    list_filter = ["severity", "status", "source"]
    search_fields = ["summary", "details"]


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "completed_at",
        "performed_by",
        "cost",
        "duration_minutes",
    ]
    list_filter = ["performed_by"]
    date_hierarchy = "completed_at"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["filename", "doc_type", "asset", "project", "created_at"]
    list_filter = ["doc_type"]
    search_fields = ["filename", "description"]

from django.urls import path

from .views.dashboard import dashboard
from .views.issue import issue_create, issue_detail, issue_edit, issue_list
from .views.project import project_create, project_detail, project_edit, project_list
from .views.schedule import (
    schedule_create,
    schedule_detail,
    schedule_edit,
    schedule_list,
    schedule_toggle_active,
)
from .views.work_log import log_work_form, quick_log

urlpatterns = [
    path("", dashboard, name="dashboard"),
    # Schedules
    path("schedules/", schedule_list, name="schedule_list"),
    path("schedules/new/", schedule_create, name="schedule_create"),
    path("schedules/<int:pk>/", schedule_detail, name="schedule_detail"),
    path("schedules/<int:pk>/edit/", schedule_edit, name="schedule_edit"),
    path("schedules/<int:pk>/toggle/", schedule_toggle_active, name="schedule_toggle_active"),
    # Projects
    path("projects/", project_list, name="project_list"),
    path("projects/new/", project_create, name="project_create"),
    path("projects/<int:pk>/", project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", project_edit, name="project_edit"),
    # Issues
    path("issues/", issue_list, name="issue_list"),
    path("issues/new/", issue_create, name="issue_create"),
    path("issues/<int:pk>/", issue_detail, name="issue_detail"),
    path("issues/<int:pk>/edit/", issue_edit, name="issue_edit"),
    # Work logs
    path("work-log/quick/<int:schedule_id>/", quick_log, name="quick_log"),
    path("work-log/form/", log_work_form, name="work_log_form"),
    path(
        "work-log/form/<int:schedule_id>/",
        log_work_form,
        name="work_log_form_for_schedule",
    ),
]

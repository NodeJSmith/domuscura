from django.urls import path

from .views.dashboard import dashboard
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
    # Work logs
    path("work-log/quick/<int:schedule_id>/", quick_log, name="quick_log"),
    path("work-log/form/", log_work_form, name="work_log_form"),
    path(
        "work-log/form/<int:schedule_id>/",
        log_work_form,
        name="work_log_form_for_schedule",
    ),
]

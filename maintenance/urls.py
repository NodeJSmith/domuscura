from django.urls import path

from .views.dashboard import dashboard
from .views.work_log import log_work_form, quick_log

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("work-log/quick/<int:schedule_id>/", quick_log, name="quick_log"),
    path("work-log/form/", log_work_form, name="work_log_form"),
    path(
        "work-log/form/<int:schedule_id>/",
        log_work_form,
        name="work_log_form_for_schedule",
    ),
]

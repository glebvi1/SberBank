from .celery import app as celery_app

__all__ = ["celery_app"]

SYSTEM_ADMIN_TEMPLATE_BASE = "system_admin/base.html"
CARD_TEMPLATE_BASE = "cards/base.html"
USER_TEMPLATE_BASE = "users/base.html"

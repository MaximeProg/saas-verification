from celery import Celery
from app.config import settings

# Créer l'instance Celery
celery_app = Celery(
    "kyc_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.image_tasks", "app.tasks.email_tasks", "app.tasks.webhook_tasks"]
)

# Configuration Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_persistent=True,
)

# Task routes désactivées pour simplifier (toutes les tasks vont dans la queue 'celery')
# celery_app.conf.task_routes = {
#     "app.tasks.image_tasks.*": {"queue": "images"},
#     "app.tasks.email_tasks.*": {"queue": "emails"},
#     "app.tasks.webhook_tasks.*": {"queue": "webhooks"},
# }

if __name__ == "__main__":
    celery_app.start()

import logging
from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.tasks_material import process_material_task
from app.workers.tasks_learning import process_quiz_completion_task

logger = logging.getLogger("study_companion.worker")

async def startup(ctx):
    logger.info("Background ARQ Worker started. Listening for tasks on Redis...")

async def shutdown(ctx):
    logger.info("Background ARQ Worker shutting down cleanly.")

class WorkerSettings:
    functions = [process_material_task, process_quiz_completion_task]
    on_startup = startup
    on_shutdown = shutdown
    # Parse redis host & port from settings.REDIS_URL
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

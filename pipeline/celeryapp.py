from celery import Celery

from pipeline.settings import BROKER_URL, BEAT_INTERVAL


app = Celery('celeryapp',
             broker=BROKER_URL,
             include=['pipeline.tasks'])

# this is helpful when you have potentially long-running tasks
app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1
)

app.conf.beat_schedule = {
    'load-data-every-30-minutes': {
        'task': 'pipeline.tasks.load_data',
        'schedule': BEAT_INTERVAL
    },
}

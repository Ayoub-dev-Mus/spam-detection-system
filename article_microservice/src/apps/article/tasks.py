from celery import shared_task

@shared_task
def my_task():
    print('Hello from Celery!')
    return 'This is a task result from Celery'
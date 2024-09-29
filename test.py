from apscheduler.schedulers.background import BackgroundScheduler
import time

# Initialize scheduler
scheduler = BackgroundScheduler()


def task():
    print("Task completed")


def start_watcher():
    """Function to schedule the watcher."""
    scheduler.start()
    # Ensure only one job is scheduled (if needed)
    if scheduler.get_jobs():
        scheduler.add_job(
            task,
            'cron',
            hour=16,
            minute=10,
        )


start_watcher()

print(scheduler.get_jobs())
while True:
    time.sleep(1)

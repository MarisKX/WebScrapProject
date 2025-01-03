from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command


def get_latest_plate():
    call_command("get_latest_plate")


def start():
    scheduler = BackgroundScheduler()
    # Add the job using the callable directly
    scheduler.add_job(
        get_latest_plate,  # Direct callable reference
        trigger=CronTrigger(hour=23, minute=55),  # Schedule at 23:55
        id="get_latest_plate",  # Unique job ID
        replace_existing=True,  # Avoid duplicates
    )
    scheduler.start()
    print("Scheduler started!")

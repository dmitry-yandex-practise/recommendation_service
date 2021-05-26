import schedule
from time import sleep
from luigi_tasks import trigger_luigi_tasks

schedule.every().day.at("23:30").do(trigger_luigi_tasks)

if __name__ == '__main__':
    trigger_luigi_tasks()
    while True:
        schedule.run_pending()
        sleep(1)

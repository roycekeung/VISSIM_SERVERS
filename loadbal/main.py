#################################################################################
#
#   Description : start of backend server on main thread
#
#################################################################################

from app import create_app

import sys
import argparse

from flask_apscheduler import APScheduler, scheduler
from taskscheduler.taskscheduler import scheduledPingTask , scheduledUnfinishedJobCheck, scheduledTaskkill


parser = argparse.ArgumentParser()
parser.add_argument('-jt', '--jobcheckTime', type=int, default=15)
parser.add_argument('-pt', '--serverPingTime', type=int, default=15)
parser.add_argument('-tkt', '--TaskkillCheckTime', type=int, default=5)
parser.add_argument('-p', '--port', type=int, default=5400)


if __name__ == '__main__':
    try:
        app= create_app()

        jobcheckTime = parser.jobcheckTime
        serverPingTime = parser.serverPingTime
        TaskkillCheckTime = parser.TaskkillCheckTime
        scheduler = APScheduler()
        scheduler.add_job(id = 'serverping', name = "check app server available", func= scheduledPingTask, trigger = 'interval', minutes = serverPingTime)
        scheduler.add_job(id = 'failedjobcheck', name = "check is job successfully sent back the results", func= scheduledUnfinishedJobCheck, trigger = 'interval', minutes = jobcheckTime)
        scheduler.add_job(id = 'bruteforceTaskkill', name = "check app is not respond and force to taskkilll from os", func= scheduledTaskkill, args = [TaskkillCheckTime], trigger = 'interval', minutes = TaskkillCheckTime)

        scheduler.start()

        app.run(host="0.0.0.0", port=parser.port, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        print ("Ctrl C - Stopping load_balancer")
        sys.exit(1)

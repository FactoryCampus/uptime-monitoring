import dbs
from ping3 import ping
import time
import sqlite3


db = dbs.DB()

HOST_EXECUTION_ID = '__SYS_HOST_DATA'
hosts = db.get_hosts(only_active=True)

nextExecution = {HOST_EXECUTION_ID: 0}

print("Started. Going into connection mode")

while True:
    try:
        # Update chached Host Data
        if nextExecution[HOST_EXECUTION_ID] < time.time():
            hosts = db.get_hosts(only_active=True)
            nextExecution[HOST_EXECUTION_ID] = time.time() + 10
        # Try connections
        for host in hosts:
            hostID = host['id']
            if hostID not in nextExecution:
                nextExecution[hostID] = 0
            if nextExecution[hostID] > time.time():
                continue  # Wait until connection should be tried
            # Set next execution first
            nextExecution[hostID] = time.time() + host['interval']
            if host['type'] == 'ping':
                c = time.time()
                t = ping(host['host'])
                if t is False:
                    db.insert_unsuccessful_ping(host['id'], c)
                else:
                    db.insert_successful_ping(host['id'], c, t)
    except sqlite3.OperationalError:
        print("Could not read or write because of Database locking, skip!")
    time.sleep(0.1)

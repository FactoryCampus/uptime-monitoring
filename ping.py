import dbs
from multiping import MultiPing
import time
import sqlite3
import requests


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
            c = time.time()
            if host['type'] == 'ping':
                mp = MultiPing([host['host']])
                try:
                    mp.send()
                    responses, noresponses = mp.receive(2)
                    if noresponses:
                        db.insert_unsuccessful_ping(host['id'], c)
                    else:
                        db.insert_successful_ping(host['id'], c, list(responses.items())[0][1])
                except OSError:
                    db.insert_unsuccessful_ping(host['id'], c)
            elif host['type'] == 'web':
                try:
                    req = requests.get(host['host'])
                    if 200 <= req.status_code <= 299:
                        db.insert_successful_ping(host['id'], c, req.elapsed.total_seconds())
                    else:
                        db.insert_unsuccessful_ping(host['id'], c)
                except requests.exceptions.ConnectionError:
                    db.insert_unsuccessful_ping(host['id'], c)
            elif host['type'] == 'incoming':
                if db.has_endpoint_entry_in_last_x_seconds(host['id'], host['interval'] * 2)['success'] == 0:
                    db.insert_unsuccessful_ping(host['id'], c)

    except sqlite3.OperationalError:
        print("Could not read or write because of Database locking, skip!")
    time.sleep(0.1)

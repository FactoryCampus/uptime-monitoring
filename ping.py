import dbs
from ping3 import ping
import time


db = dbs.DB()

while True:
    for host in db.get_hosts():
        if host['type'] == 'ping':
            c = time.time()
            t = ping(host['host'])
            if t is False:
                db.insert_unsuccessful_ping(host['id'], c)
            else:
                db.insert_successful_ping(host['id'], c, t)
    time.sleep(2)

import dbs
from ping3 import ping
import time


db = dbs.DB()

while True:
    for host in db.get_hosts():
        if host[2] == 'ping':
            c = time.time()
            t = ping(host[1])
            if t is False:
                db.insert_unsuccessful_ping(host[0], c)
            else:
                db.insert_successful_ping(host[0], c, t)
    time.sleep(2)

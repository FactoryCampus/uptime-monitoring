# This script should be run via a cron (e.g. every minute)

import dbs
import requests
import os


def send_notification(endpoint, down):
    name = endpoint['alias'] + " (" + endpoint['host'] + ")" if endpoint['alias'] is not None else endpoint['host']
    if 'UPTIME_MONITOR_SLACK_URL' in os.environ:
        requests.post(
            os.environ['UPTIME_MONITOR_SLACK_URL'],
            json={'text': name + (" is Down :(" if down else " is Up :)")}
        )


db = dbs.DB()

hosts = db.get_hosts(only_active=True)

for host in hosts:
    requiredCount = 2 if host['interval'] > 10 else 5
    isDown = db.conn.execute(
        'SELECT (count(*) - count(responseTime) > ?) AS isUp FROM (SELECT * FROM history WHERE endpoint=? ORDER BY startedOn DESC LIMIT ? * 2)',
        (requiredCount, host['id'], requiredCount)) \
        .fetchall()[0]['isDown']
    if isDown == 1:
        if not db.endpoint_has_active_notification(host['id']):
            db.endpoint_add_active_notification(host['id'])
            send_notification(host, down=True)
    else:
        if db.endpoint_has_active_notification(host['id']):
            db.endpoint_disable_active_notifications(host['id'])
            send_notification(host, down=False)

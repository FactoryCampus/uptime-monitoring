import os

from flask import Flask, render_template, redirect, request, session
import json

import dbs
import hashlib
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.getenv('UPTIME_MONITOR_SECRET')


@app.route('/')
def index():
    if session is not None and 'authenticated' in session and session['authenticated']:
        return redirect('/downtimes')
    return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html.twig')


@app.route('/login', methods=['POST'])
def login_post():
    if 'username' not in request.form or 'password' not in request.form:
        return redirect('/login', 400)
    if request.form['username'] == 'admin' and \
         hashlib.sha1(request.form['password'].encode()).hexdigest() == os.getenv('UPTIME_MONITOR_PASSWORD'):
        session['authenticated'] = True
        return redirect('/downtimes')
    else:
        session['authenticated'] = False
        return redirect('/', 403)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['authenticated'] = False
    return redirect('/')


@app.route('/downtimes')
def downtimes():
    if ('authenticated' not in session) or (not session['authenticated'] is True):
        return redirect('/login', 403)
    db = dbs.DB()
    data = db.get_unsuccessful_connections_today()
    template_data = {}
    for downtime in data:
        start = datetime.fromtimestamp(int(downtime['startedOn'])).strftime('%H:%M:%S')
        if start not in template_data:
            template_data[start] = {'hosts': []}
        template_data[start]['hosts'].append(downtime['host'])
    return render_template('downtimes.html.twig', downtime=template_data)


@app.route('/uptimes')
def uptimes():
    if ('authenticated' not in session) or (not session['authenticated'] is True):
        return redirect('/login', 403)
    db = dbs.DB()
    return render_template('uptimes_list.html.twig', endpoints=db.get_endpoints_with_failed_requests_data())


@app.route('/uptimes/<endpoint>')
def uptimes_endpoint(endpoint):
    if ('authenticated' not in session) or (not session['authenticated'] is True):
        return redirect('/login', 403)
    db = dbs.DB()
    return render_template('uptimes_entry.html.twig',
                           id=endpoint,
                           downTime24=db.get_count_failed_requests_time_in_the_last_x_seconds(endpoint, 60 * 60 * 24),
                           downTime7days=db.get_count_failed_requests_time_in_the_last_x_seconds(endpoint, 60 * 60 * 24 * 7),
                           downTimeMonth=db.get_count_failed_requests_time_in_the_last_x_seconds(endpoint, 60 * 60 * 24 * 31),
                           downtime=db.get_unsuccessful_connections_today(endpoint=endpoint)
                           )


@app.route('/api/downtimes')
def downtimes_api():
    if not session['authenticated'] is True:
        return redirect('/login', 403)
    db = dbs.DB()
    return json.dumps(db.get_unsuccessful_connections_today())


@app.route('/endpoints', methods=['GET'])
def hosts():
    if ('authenticated' not in session) or (not session['authenticated'] is True):
        return redirect('/login', 403)
    db = dbs.DB()
    hosts = db.get_hosts()
    return render_template('hosts.html.twig', hosts=hosts)


@app.route('/endpoints', methods=['POST'])
def add_edit_hosts():
    # check logged in
    if ('authenticated' not in session) or (not session['authenticated'] is True):
        return redirect('/login', 403)
    db = dbs.DB()
    # check if all is there
    if 'host' not in request.form or 'alias' not in request.form or ('id' in request.form and 'interval' not in request.form):
        return redirect('/endpoints', 400)
    # Set alias
    alias = None
    if request.form['alias'] != '' and request.form['alias'] != 'None':
        alias = request.form['alias']
    # update
    if 'id' in request.form:
        db.update_endpoint(request.form['id'], request.form['host'], alias, request.form['interval'], 'active' in request.form)
    # create
    else:
        if 'type' not in request.form or (request.form['type'] != 'web' and request.form['type'] != 'ping'):
            return redirect('/endpoints', 400)
        db.add_endpoint_host(request.form['host'], alias, request.form['type'])
    # redirect
    return redirect('/endpoints')


@app.template_filter('otime')
def otime(s):
    return datetime.utcfromtimestamp(int(s)).strftime('%H:%M:%S')

if __name__ == '__main__':
    app.run(host='0.0.0.0')

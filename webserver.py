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
    if not session['authenticated'] is True:
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


@app.route('/api/downtimes')
def downtimes_api():
    if not session['authenticated'] is True:
        return redirect('/login', 403)
    db = dbs.DB()
    return json.dumps(db.get_unsuccessful_connections_today())


if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import Flask, render_template
import json
import dbs
from datetime import datetime
app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/downtimes')


@app.route('/downtimes')
def downtimes():
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
    db = dbs.DB()
    return json.dumps(db.get_unsuccessful_connections_today())

if __name__ == '__main__':
    app.run()
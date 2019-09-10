from flask import Flask, jsonify
from flask_cors import CORS
from pyzabbix import ZabbixAPI
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask("zabbix")
CORS(app)

with open("credentials.json", "r") as file:
    credentials = json.load(file)

url = credentials['url']
username = credentials['username']
password = credentials['password']
zapi = ZabbixAPI(url)

# Disable SSL certificate verification
zapi.session.verify = False

zapi.login(username, password)


@app.route('/')
def index():
    return 'Server works!'


@app.route('/hosts')
def getHosts():
    # hosts = zapi.host.get(output=['hostid', 'host', 'name', 'status'])
    hosts = zapi.host.get()
    # hosts = [host for host in hosts if not host['hostid'] == '11520']
    return jsonify(hosts)


@app.route('/status')
def getErrors():
    jsonreturn = []
    errors = zapi.trigger.get(only_true=1,
                              skipDependent=1,
                              monitored=1,
                              active=1,
                              selectHosts=['name'],
                              min_severity=2)

    for error in errors:
        timestamp = datetime.fromtimestamp(int(error['lastchange']))
        jsonreturn.append({
            "triggerid": error['triggerid'],
            "error": error['description'],
            "location": error["hosts"][0]["name"],
            "date": timestamp.strftime("%a %b %d"),
            "time": timestamp.strftime("%X")})
    return jsonify(jsonreturn)

# @app.route('/history')
def getHistoricalTriggers():
    history = zapi.event.get(objectids="58008")
    print(history)

getHistoricalTriggers()


def hostStatus():
    enabled = 0
    disabled = 0
    hosts = getHosts()
    for host in hosts:
        if host['status'] == '0':
            enabled += 1
        else:
            disabled += 1
    # with open('../frontend/src/data/hoststatus.json', 'w') as file:
    #     json.dump({'enabled': enabled, 'disabled': disabled, 'total': len(hosts)}, file)
    # with open('../frontend/src/data/hosts.json', 'w') as file:
    #     json.dump(hosts, file)
    return hosts


if __name__ == '__main__':
    app.run(debug=True)

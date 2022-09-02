from flask import Flask
import json
import click
import time
import requests
import threading
import logging
from systemd.journal import JournalHandler

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

heartbeat_period: float = None
prev_heartbeat: float = None
action_url: str = None


def check_heartbeat():
    global prev_heartbeat
    threading.Timer(heartbeat_period, check_heartbeat).start()
    if prev_heartbeat is None:
        log.info('Starting listening for heartbeats.')
        prev_heartbeat = time.time()
    else:
        prev_heartbeat_age = time.time() - prev_heartbeat
        log.info(f'Last heartbeat received {prev_heartbeat_age:9.2f} seconds ago.')
        if prev_heartbeat_age >= heartbeat_period:
            requests.get(action_url)


@click.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=80)
@click.option('--period', default=60)
@click.option('--url', default="test_url")
def create_app(host, port, period, url):
    global heartbeat_period, action_url
    heartbeat_period = period
    action_url = url
    check_heartbeat()
    app = Flask(__name__)

    @app.route("/")
    @click.argument("url")
    @click.argument("period")
    def run():
        global prev_heartbeat
        prev_heartbeat = time.time()
        log.info('Heartbeat received.')
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    app.run(host=host, port=port)


if __name__ == '__main__':
    create_app()

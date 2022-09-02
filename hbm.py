from flask import Flask
import json
import click
import time
import requests
import threading

heartbeat_period: float
action_url: str
prev_heartbeat = time.time()


def check_heartbeat():
    global prev_heartbeat
    threading.Timer(heartbeat_period, check_heartbeat).start()
    prev_heartbeat_age = time.time() - prev_heartbeat
    print(f'Previous heartbeat was received {prev_heartbeat_age} seconds ago.')
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
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    app.run(host=host, port=port)


if __name__ == '__main__':
    create_app()

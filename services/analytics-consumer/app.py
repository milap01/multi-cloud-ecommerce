#2025H1030231P

import os
import json
from flask import Flask, jsonify
from threading import Thread

from azure.eventhub import EventHubConsumerClient

app = Flask(__name__)

# store latest metric in memory
latest_metric = {"unique_users": 0, "window_start": None, "window_end": None}

EVENT_HUB_CONN_STR = os.environ.get("EVENT_HUB_CONN_STR_RESULTS")
EVENT_HUB_NAME = "results"
CONSUMER_GROUP = "$Default"


def on_event(partition_context, event):
    global latest_metric
    body = event.body_as_str()
    try:
        data = json.loads(body)
        latest_metric = data
        print("Received result:", data)
    except json.JSONDecodeError:
        print("Bad JSON from Flink:", body)

    partition_context.update_checkpoint(event)


def start_consumer():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONN_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME,
    )

    with client:
        client.receive(
            on_event=on_event,
            starting_position="-1",  # from beginning
        )


@app.route("/metrics")
def metrics():
    return jsonify(latest_metric)


if __name__ == "__main__":
    # run consumer in background thread
    t = Thread(target=start_consumer, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=8000)

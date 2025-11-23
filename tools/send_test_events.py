# 2025H1030231P

import os
import time
import json
import random
from azure.eventhub import EventHubProducerClient, EventData

EVENT_HUB_CONN_STR = os.environ.get("EVENT_HUB_CONN_STR_EVENTS")
EVENT_HUB_NAME = "events"

users = ["u1", "u2", "u3", "u4", "u5"]
event_types = ["view_product", "add_to_cart", "purchase"]


def main():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONN_STR,
        eventhub_name=EVENT_HUB_NAME
    )

    while True:
        user_id = random.choice(users)
        event_type = random.choice(event_types)
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": int(time.time())
        }
        event_data = EventData(json.dumps(payload))
        print("Sending event:", payload)
        with producer:
            producer.send_batch([event_data])

        time.sleep(1)  # send 1 event per second


if __name__ == "__main__":
    main()

#2025H1030231P
import json
import time

from pyflink.datastream import (
    StreamExecutionEnvironment,
    TimeCharacteristic
)
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common.typeinfo import Types
from pyflink.common.time import Time
from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common.watermark_strategy import WatermarkStrategy

# NOTE: In actual deployment, you will configure the Kafka-compatible
# Event Hubs connector via Flink's KafkaSource / KafkaSink
# Here we focus on the window logic + transformation.


class UniqueUsersPerWindow(ProcessWindowFunction):

    def process(self, key, context, elements, out):
        """
        key: window key (we use a constant, so global aggregation)
        context: gives window start/end
        elements: all events in the window
        out: collector to emit results
        """
        users = set()
        for e in elements:
            users.add(e["user_id"])

        result = {
            "window_start": context.window().start,
            "window_end": context.window().end,
            "unique_users": len(users),
            "event_count": len(list(elements))
        }
        out.collect(json.dumps(result))


def parse_event(json_str: str):
    """
    Parse the incoming JSON string and normalize fields.
    """
    try:
        e = json.loads(json_str)
    except json.JSONDecodeError:
        # ignore bad messages
        return None

    # Ensure required fields
    if "user_id" not in e:
        return None

    if "timestamp" not in e:
        e["timestamp"] = int(time.time())

    return e


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)

    # Use event time if you want precise time semantics
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

    # ========================
    # Configure Event Hubs (Kafka-compatible) source & sink
    # ========================

    # These would be passed via env variables/configs in real deployments
    event_hubs_kafka_bootstrap = "mce-streams.servicebus.windows.net:9093"
    event_hubs_sasl_username = "$ConnectionString"
    event_hubs_sasl_password = "<EVENT_HUBS_CONNECTION_STRING>"  # set at deployment
    input_topic = "events"
    output_topic = "results"
    consumer_group = "$Default"

    from pyflink.datastream.connectors.kafka import (
        KafkaSource,
        KafkaSink,
        KafkaRecordSerializationSchema
    )
    from pyflink.common.serialization import SimpleStringSchema

    # Source: Event Hubs as Kafka
    source = (
        KafkaSource.builder()
        .set_bootstrap_servers(event_hubs_kafka_bootstrap)
        .set_topics(input_topic)
        .set_group_id(consumer_group)
        .set_value_only_deserializer(SimpleStringSchema())
        .set_property("security.protocol", "SASL_SSL")
        .set_property("sasl.mechanism", "PLAIN")
        .set_property(
            "sasl.jaas.config",
            f'org.apache.kafka.common.security.plain.PlainLoginModule required '
            f'username="{event_hubs_sasl_username}" '
            f'password="{event_hubs_sasl_password}";'
        )
        .build()
    )

    # Create DataStream from source with watermarks (simple strategy)
    watermark_strategy = (
        WatermarkStrategy
        .for_monotonous_timestamps()
        .with_timestamp_assigner(lambda e, ts: int(e["timestamp"]) * 1000)
    )

    events_stream = (
        env.from_source(
            source,
            watermark_strategy,
            "event-hubs-events"
        )
        .map(parse_event, output_type=Types.PICKLED_BYTE_ARRAY())  # simplified
        .filter(lambda e: e is not None)
    )

    # Window: 1 minute tumbling, global key (we use constant value 1)
    windowed = (
        events_stream
        .key_by(lambda e: 1)
        .window(TumblingEventTimeWindows.of(Time.minutes(1)))
        .process(UniqueUsersPerWindow(), output_type=Types.STRING())
    )

    # Sink: Event Hubs "results" topic as Kafka sink
    sink = (
        KafkaSink.builder()
        .set_bootstrap_servers(event_hubs_kafka_bootstrap)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(output_topic)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        .set_property("security.protocol", "SASL_SSL")
        .set_property("sasl.mechanism", "PLAIN")
        .set_property(
            "sasl.jaas.config",
            f'org.apache.kafka.common.security.plain.PlainLoginModule required '
            f'username="{event_hubs_sasl_username}" '
            f'password="{event_hubs_sasl_password}";'
        )
        .build()
    )

    windowed.sink_to(sink)

    env.execute("UniqueUsersPerMinute")


if __name__ == "__main__":
    main()


import os
import json
from pyflink.common import SimpleStringSchema, Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time

def process_orders():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Azure Event Hubs (Kafka) Configuration
    # These should be loaded from env vars in production
    event_hub_namespace = "mce-events-ns-mce" # From your terraform
    connection_string = os.environ.get("EVENT_HUB_CONN_STRING")
    
    # SASL Config for Azure
    sasl_config = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{connection_string}";'

    kafka_props = {
        'bootstrap.servers': f'{event_hub_namespace}.servicebus.windows.net:9093',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.jaas.config': sasl_config,
        'group.id': 'flink-group'
    }

    # Consumer: Read from 'orders' (mapped to 'analytics-topic' Event Hub)
    consumer = FlinkKafkaConsumer(
        topics='analytics-topic', 
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    consumer.set_start_from_earliest()

    # Processing: Count orders per minute
    ds = env.add_source(consumer)
    
    def parse_order(data):
        try:
            return ("order", 1)
        except:
            return ("error", 0)

    stats = ds \
        .map(parse_order, output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda x: x[0]) \
        .window(TumblingProcessingTimeWindows.of(Time.minutes(1))) \
        .sum(1) \
        .map(lambda x: json.dumps({"type": "1min-agg", "count": x[1]}), output_type=Types.STRING())

    # Producer: Write back to a separate topic/hub (e.g., 'stats-topic')
    # For now, just print to stdout to verify logic if you don't have a 2nd hub
    stats.print()

    env.execute("Azure Event Hubs Flink Job")

if __name__ == '__main__':
    process_orders()
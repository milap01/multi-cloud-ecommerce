import os
import json
from pyflink.common import SimpleStringSchema, Types, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time

def process_orders():
    # 1. Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_stream_time_characteristic(TimeCharacteristic.ProcessingTime)
    
    # Ensure you pass the kafka jar when submitting the job!
    # e.g. --jar flink-sql-connector-kafka-*.jar

    # 2. Configure Kafka Properties
    # NOTE: Replace with your actual MSK Bootstrap servers string
    kafka_props = {
        'bootstrap.servers': 'b-1.mce-msk-xxxx.kafka.us-east-1.amazonaws.com:9092,b-2...',
        'group.id': 'flink-order-group'
    }

    # 3. Define the Source (Consumer)
    # Consuming from the 'orders' topic produced by your Order Service
    kafka_consumer = FlinkKafkaConsumer(
        topics='orders',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    kafka_consumer.set_start_from_earliest()

    # 4. Define the Data Stream
    ds = env.add_source(kafka_consumer)

    # 5. Transformation Logic
    # Parse JSON, map to (1, 1) tuple for counting, window, and sum
    # Assuming order looks like {"id": "...", "total": 100, ...}
    
    def parse_order(data):
        try:
            order = json.loads(data)
            # Return a tuple: (constant_key, count)
            return ("all_orders", 1)
        except:
            return ("error", 0)

    aggregated_stream = ds \
        .map(parse_order, output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda x: x[0]) \
        .window(TumblingProcessingTimeWindows.of(Time.minutes(1))) \
        .sum(1) \
        .map(lambda x: json.dumps({"window_type": "1min", "count": x[1]}), output_type=Types.STRING())

    # 6. Define the Sink (Producer)
    # Publishing aggregated stats to 'order-stats' topic
    kafka_producer = FlinkKafkaProducer(
        topic='order-stats',
        serialization_schema=SimpleStringSchema(),
        producer_config=kafka_props
    )

    aggregated_stream.add_sink(kafka_producer)

    # 7. Execute
    env.execute("Order Aggregation Job")

if __name__ == '__main__':
    process_orders()
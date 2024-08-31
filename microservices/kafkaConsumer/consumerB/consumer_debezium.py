from kafka import KafkaConsumer
from confluent_kafka import Consumer, KafkaError, KafkaException
import json
import time

## Native implement
# def consume_topic_a():
#     consumer = KafkaConsumer(
#         'topic_a',
#         bootstrap_servers='kafka:9092',
##        bootstrap_servers='localhost:29092',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#         auto_offset_reset='earliest',
#         enable_auto_commit=True,
#         request_timeout_ms=120000 # 120s timeout
#     )
#
#     for message in consumer:
#         with open('topic_a_data.json', 'a') as f:
#             json.dump(message.value, f)
#             f.write('\n')  # Write each message on a new line
#
# def consume_topic_b():
#     consumer = KafkaConsumer(
#         'dbserver1.public.weather',  # Topic created by Debezium
#         bootstrap_servers='kafka:9092',
##        bootstrap_servers='localhost:29092',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#         auto_offset_reset='earliest',
#         enable_auto_commit=True,
#         request_timeout_ms=120000 # 120s timeout
#     )
#
#     for message in consumer:
#         with open('topic_b_data.json', 'a') as f:
#             json.dump(message.value, f)
#             f.write('\n')  # Write each message on a new line
#
# if __name__ == "__main__":
#     consume_topic_a()
#     consume_topic_b()

## Confluent Kafka implement

## for only 1 topic, define other topic b...
def consume_topic_a():
    print('Consumer started to consume from topics')
    consumer = Consumer({
        # 'bootstrap.servers': 'localhost:29092',  # Use the host port for local testing
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'debezium_group',
        'auto.offset.reset': 'earliest'
    })

    topic = 'dbserver1.public.weather'
    while True:
        try:
            # Attempt to subscribe to the topic
            consumer.subscribe([topic])
            while True:
                msg = consumer.poll(1.0)  # Timeout of 1 second
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        print(f"Topic '{topic}' not found. Retrying...")
                        break  # Exit inner loop to retry subscribing
                    else:
                        print(f"Error: {msg.error()}")
                        break
                else:
                    # Process the message and dump it to the mounted directory
                    with open('/data/debezium_data.json', 'a') as f:  # Save to /data inside the container
                        json.dump(msg.value().decode('utf-8'), f)
                        f.write('\n')  # Write each message on a new line
        except KafkaException as e:
            print(f"Kafka exception occurred: {e}")
        # Wait for a few seconds before trying to subscribe again
        time.sleep(5)

if __name__ == "__main__":
    consume_topic_a()

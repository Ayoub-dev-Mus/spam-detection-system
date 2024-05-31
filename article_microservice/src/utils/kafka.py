import json
import os
from confluent_kafka import Producer, Consumer

class KafkaUtils:
    def __init__(self):
       self.producer = Producer({
            'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
            'sasl.mechanism': os.getenv('SASL_MECHANISM'),
            'security.protocol': os.getenv('SECURITY_PROTOCOL'),
            'sasl.username': os.getenv('SASL_USERNAME'),
            'sasl.password': os.getenv('SASL_PASSWORD')
        })

       self.consumer = Consumer({
            'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
            'sasl.mechanism': os.getenv('SASL_MECHANISM'),
            'security.protocol': os.getenv('SECURITY_PROTOCOL'),
            'sasl.username': os.getenv('SASL_USERNAME'),
            'sasl.password': os.getenv('SASL_PASSWORD'),
            'group.id': os.getenv('GROUP_ID'),
            'auto.offset.reset': os.getenv('AUTO_OFFSET_RESET')
        })

    def produce_message(self, key, message):
        try:

            serialized_message = json.dumps(message).encode('utf-8')


            self.producer.produce('created_articles', key=key, value=serialized_message)
            self.producer.flush()
            print("Message produced to Kafka!")
        except Exception as e:
            print(f"Error producing message: {e}")

    def consume_messages(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                print(f"Received message: {msg.value().decode('utf-8')}")
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

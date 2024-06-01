import json
from confluent_kafka import Producer, Consumer

class KafkaUtils:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
            'sasl.mechanism': 'SCRAM-SHA-256',
            'security.protocol': 'SASL_SSL',
            'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
            'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz'
        })

        self.consumer = Consumer({
            'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
            'sasl.mechanism': 'SCRAM-SHA-256',
            'security.protocol': 'SASL_SSL',
            'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
            'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz',
            'group.id': 'YOUR_CONSUMER_GROUP', 
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe(['spam_articles'])

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

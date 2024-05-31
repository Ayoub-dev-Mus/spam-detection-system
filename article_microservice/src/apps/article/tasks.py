from celery import shared_task
from utils.kafka import KafkaUtils
import json
from .views import update_article_in_db  

@shared_task
def process_message():
    kafka_utils = KafkaUtils()

    def process_message_content(message):
        try:
            article_data = json.loads(message)
            article_id = article_data.get("article_id")
            is_spam = article_data.get("is_spam")

            if article_id is not None and is_spam is not None:
                result = update_article_in_db(article_id, is_spam)
                if "error" in result:
                    print(f"Failed to update article {article_id}: {result['error']}")
                else:
                    print(f"Article {article_id} updated successfully.")
        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")

    try:
        while True:
            msg = kafka_utils.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            message_value = msg.value().decode('utf-8')
            print(f"Received message: {message_value}")
            process_message_content(message_value)
    except KeyboardInterrupt:
        pass
    finally:
        kafka_utils.consumer.close()

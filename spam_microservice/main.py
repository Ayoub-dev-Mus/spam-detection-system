from fastapi import FastAPI, BackgroundTasks
from confluent_kafka import Producer, Consumer
from typing import List
import pickle
import json
from sklearn.feature_extraction.text import CountVectorizer
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

app = FastAPI()

producer = Producer({
    'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
    'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz'
})

consumer = Consumer({
    'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
    'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz',
    'group.id': 'YOUR_CONSUMER_GROUP',
    'auto.offset.reset': 'earliest'
})

model = None
vectorizer = None

def load_model_and_vectorizer():
    global model, vectorizer
    with open('./model_script/spam_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('./model_script/vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)

load_model_and_vectorizer()

def process_messages(messages: List[dict]):
    contents = [message['content'] for message in messages]
    article_ids = [message['article_id'] for message in messages] 
    transformed_messages = vectorizer.transform(contents)
    predictions = model.predict(transformed_messages)
    return [
        {"article_id": article_id, "is_spam": bool(pred)}
        for article_id, pred in zip(article_ids, predictions)
    ]

async def kafka_consumer_task():
    consumer.subscribe(['created_articles'])
    try:
        while True:
            new_messages = []
            while len(new_messages) < 2:
                msg = consumer.poll(1.0)
                if msg is None:
                    await asyncio.sleep(1)
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                message_value = msg.value().decode('utf-8')
                new_messages.append(json.loads(message_value))
                print(message_value)

            predictions = process_messages(new_messages)

            for prediction in predictions:
                producer.produce('spam_articles', key=None, value=json.dumps(prediction).encode('utf-8'))
                producer.flush()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        consumer.close()
        print("Consumer closed")

class ModelFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('spam_model.pkl') or event.src_path.endswith('vectorizer.pkl'):
            print(f"File {event.src_path} changed, reloading model and vectorizer.")
            load_model_and_vectorizer()

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    loop.create_task(kafka_consumer_task())
    print("Kafka consumer task added to background tasks")

    event_handler = ModelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./model_script', recursive=False)
    observer.start()
    app.state.observer = observer
    print("File observer started")

@app.on_event("shutdown")
async def shutdown_event():
    observer = app.state.observer
    observer.stop()
    observer.join()
    print("File observer stopped")

@app.get("/")
async def root():
    return {"message": "Spam Microservice"}

@app.post("/reload_model")
async def reload_model():
    load_model_and_vectorizer()
    return {"message": "Model and vectorizer reloaded successfully."}

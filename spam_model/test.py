from fastapi import FastAPI
from confluent_kafka import Producer, Consumer
from typing import List
import pickle
from sklearn.feature_extraction.text import CountVectorizer

app = FastAPI()

# Initialize Kafka producer
producer = Producer({
    'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
    'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz'
})

# Initialize Kafka consumer
consumer = Consumer({
    'bootstrap.servers': 'caring-doe-7639-eu2-kafka.upstash.io:9092',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'Y2FyaW5nLWRvZS03NjM5JP4WoxPA580OXpol6ekTROh7p0av-gUPRHqRk6Q8CSk',
    'sasl.password': 'ZTNmNzFhMzYtMjUwYy00MzViLWFhOGUtNmZlOTlmNGY4YTAz',
    'group.id': 'YOUR_CONSUMER_GROUP',
    'auto.offset.reset': 'earliest'
})


with open('spam_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

def process_messages(messages: List[str]):
    transformed_messages = vectorizer.transform(messages)
    predictions = model.predict(transformed_messages)
    return predictions.tolist()

@app.get("/")
async def root():
    return {"message": "Welcome to Kafka FastAPI"}

@app.get("/consume_process_produce")
async def consume_process_produce():
    new_messages = []

    consumer.subscribe(['created_articles'])

    for message in consumer:
        new_messages.append(message.value().decode('utf-8'))
        print(message.value().decode('utf-8'))
        if len(new_messages) >= 2:
            break


    predictions = process_messages(new_messages)


    for prediction in predictions:
        producer.produce('spam_articles', str(prediction).encode('utf-8'))

    return {"message": "Messages consumed, processed, and republished."}

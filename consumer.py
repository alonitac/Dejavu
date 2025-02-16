import os
import json
import pika
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer

config = {
    "database": {
        "host": os.getenv("DB_HOST", "db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "database": os.getenv("DB_NAME", "dejavu")
    },
    "database_type": os.getenv("DB_TYPE", "postgres")
}

djv = Dejavu(config)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "audio_queue"

def process_audio(ch, method, properties, body):
    """Process audio file received from RabbitMQ."""
    message = json.loads(body)
    audio_file = message.get("audio_file")

    if not audio_file:
        print("Received empty audio file path.")
        return

    print(f"Processing: {audio_file}")

    try:
        results = djv.recognize(FileRecognizer, audio_file)
        print(f"Recognition result: {results}")

    except Exception as e:
        print(f"Error recognizing {audio_file}: {e}")

def start_consumer():
    """Start RabbitMQ consumer."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_audio, auto_ack=True)

    print(f"[*] Waiting for audio files on {QUEUE_NAME}...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()

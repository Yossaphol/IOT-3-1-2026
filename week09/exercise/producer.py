import pika
import json
import time
import random
import ssl
from datetime import datetime

# -----------------------------
# RabbitMQ Configuration
# -----------------------------
RABBITMQ_HOST = "amqp.iot.kmitl.co"
RABBITMQ_USER = "67070145"
RABBITMQ_PASS = "P7AEEAgEuCgJ-HBhO9kYO1ED8QUwCrbP"

EXCHANGE_NAME = "my-exchange-1"
EXCHANGE_TYPE = "direct"

ROUTING_KEY = "info"


# -----------------------------
# Connect RabbitMQ
# -----------------------------
credentials = pika.PlainCredentials(
    RABBITMQ_USER,
    RABBITMQ_PASS
)

parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    credentials=credentials,
    port=5671,
    virtual_host="67070145",
    ssl_options=pika.SSLOptions(
        ssl.create_default_context()   # verifies broker cert against system CAs
    )
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()


# -----------------------------
# Declare Exchange
# -----------------------------
channel.exchange_declare(
    exchange=EXCHANGE_NAME,
    exchange_type=EXCHANGE_TYPE,
    durable=True
)


print("Producer started")
print("Press Ctrl+C to stop\n")


try:

    while True:
        temperature = round(random.uniform(70, 105), 1)
        vibration = round(random.uniform(2.0, 8.0), 2)
        current = round(random.uniform(8, 15), 2)

        data = {
            "machine_id": "M01",
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "vibration": vibration,
            "current": current
        }

        message = json.dumps(data)

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=message,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
            )
        )

        print(f"[SEND] {message}")

        time.sleep(2)


except KeyboardInterrupt:
    print("\nStopping Producer...")

finally:
    connection.close()
import pika
import json
import ssl

# -----------------------------
# RabbitMQ Configuration
# -----------------------------
RABBITMQ_HOST = "amqp.iot.kmitl.co"
RABBITMQ_USER = "รหัส นศ"
RABBITMQ_PASS = "ค่าที่กำหนดให้"

EXCHANGE_NAME = "amq.direct"
EXCHANGE_TYPE = "direct"

QUEUE_NAME = "direct.red"

ROUTING_KEY = "red"


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
    virtual_host="/",
    ssl_options=pika.SSLOptions(
        ssl.create_default_context()   # verifies broker cert against system CAs
    )
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()


# -----------------------------
# Exchange
# -----------------------------
channel.exchange_declare(
    exchange=EXCHANGE_NAME,
    exchange_type=EXCHANGE_TYPE,
    durable=True
)


# -----------------------------
# Queue
# -----------------------------
channel.queue_declare(
    queue=QUEUE_NAME,
    durable=True
)


# -----------------------------
# Binding
# -----------------------------
channel.queue_bind(
    exchange=EXCHANGE_NAME,
    queue=QUEUE_NAME,
    routing_key=ROUTING_KEY
)


# -----------------------------
# ACK / Retry
# -----------------------------
def callback(ch, method, properties, body):

    try:

        data = json.loads(body)

        machine = data["machine_id"]
        temperature = data["temperature"]
        vibration = data["vibration"]

        print("\n[RECEIVE]")
        print(f"Machine     : {machine}")
        print(f"Temperature : {temperature} °C")
        print(f"Vibration   : {vibration} mm/s")

        # -------------------------
        # ตรวจสอบความผิดปกติ
        # -------------------------
        if temperature > 95:

            print("!!! ALARM !!!")
            print("Temperature too high")

            # สมมติว่าประมวลผลสำเร็จ
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

            print("[ACK] Message processed")

        else:

            print("Normal")

            # ประมวลผลสำเร็จ
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

            print("[ACK] Message processed")


    except Exception as e:

        print(f"[ERROR] {e}")

        # Processing ไม่สำเร็จ
        # ให้ RabbitMQ ส่งกลับ Queue
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True
        )

        print("[RETRY] Message returned to queue")


# -----------------------------
# Start Consumer
# -----------------------------
channel.basic_qos(
    prefetch_count=1
)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=False
)


print("Consumer started")
print(f"Queue       : {QUEUE_NAME}")
print(f"Routing Key : {ROUTING_KEY}")
print("Waiting for messages...\n")


try:

    channel.start_consuming()

except KeyboardInterrupt:

    print("\nStopping Consumer...")
    channel.stop_consuming()

finally:

    connection.close()
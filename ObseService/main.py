import pika
import time
import os
from datetime import datetime

BROKER_NAME = 'broker_service'
EXCHANGE = 'topic_exchange'
ROUTING_KEY = 'my.*'
OBSE_QUEUE = 'obse_queue'
LOG_FILE_PATH = '/output/logs.txt'


def establish_connection(retries=0):
    try:
        return pika.BlockingConnection(pika.ConnectionParameters(BROKER_NAME))
    except pika.exceptions.AMQPConnectionError as e:
        if retries > 10:
            raise e

        time.sleep(2)
        return establish_connection(retries=retries + 1)


def on_message(channel, method, properties, body):
    timestamp = datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + 'Z'
    topic = method.routing_key
    message = body.decode('utf-8')

    log_message = '{timestamp} Topic {topic}: {message}\n'.format(
        timestamp=timestamp,
        topic=topic,
        message=message
    )
    print(log_message)

    f = open(LOG_FILE_PATH, "a")
    f.write(log_message)
    f.close()


def main():
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)

    connection = establish_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=OBSE_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=OBSE_QUEUE, routing_key=ROUTING_KEY)

    channel.basic_consume(queue=OBSE_QUEUE,
                          auto_ack=True,
                          on_message_callback=on_message)

    channel.start_consuming()

try:
    main()
except KeyboardInterrupt:
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

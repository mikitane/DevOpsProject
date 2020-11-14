import pika
import time
import os

BROKER_NAME = 'broker_service'
EXCHANGE = 'topic_exchange'
CONSUME_ROUTING_KEY = 'my.o'
PUBLISH_ROUTING_KEY = 'my.i'
IMED_QUEUE = 'imed_queue'


def establish_connection(retries=0):
    try:
        return pika.BlockingConnection(pika.ConnectionParameters(BROKER_NAME))
    except pika.exceptions.AMQPConnectionError as e:
        if retries > 10:
            raise e

        time.sleep(2)
        return establish_connection(retries=retries + 1)


def on_message(channel, method, properties, body):
    time.sleep(1)

    orig_message = body.decode('utf-8')
    new_message = 'Got {}'.format(orig_message)

    channel.basic_publish(exchange=EXCHANGE,
                          routing_key=PUBLISH_ROUTING_KEY,
                          body=new_message)


def main():
    connection = establish_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=IMED_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=IMED_QUEUE, routing_key=CONSUME_ROUTING_KEY)

    channel.basic_consume(queue=IMED_QUEUE,
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

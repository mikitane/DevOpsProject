# ImedService is responsible for handling two
# different tasks: listening for messages with
# my.o routing key and publishing a modified
# message with my.i routing key.

import pika
import time
import os

# Internal domain name of the RabbitMQ service
BROKER_NAME = 'broker_service'

# Exchange to which all the queues this service uses
# are binded to.
EXCHANGE = 'topic_exchange'

# Handle all messages with this routing key
CONSUME_ROUTING_KEY = 'my.o'

# Publish new messages with this routing key
PUBLISH_ROUTING_KEY = 'my.i'

# Name of the queue that this service uses
IMED_QUEUE = 'imed_queue'

# Setup for the queues of ObseService
OBSE_QUEUE = 'obse_queue'
WILDCARD_ROUTING_KEY = 'my.*'

# Establish connection to RabbitMQ service
# If failed, retry 10 times before throwing exception.
def establish_connection(retries=0):
    try:
        return pika.BlockingConnection(pika.ConnectionParameters(BROKER_NAME))
    except pika.exceptions.AMQPConnectionError as e:
        if retries > 10:
            raise e

        time.sleep(2)
        return establish_connection(retries=retries + 1)

# Handler for messages published with my.o routing key
def on_message(channel, method, properties, body):
    time.sleep(1)

    orig_message = body.decode('utf-8')

    # Prefix the original message with Got
    new_message = 'Got {}'.format(orig_message)

    # Publish the prefixed message with my.i routing key
    channel.basic_publish(exchange=EXCHANGE,
                          routing_key=PUBLISH_ROUTING_KEY,
                          body=new_message)


# This function is executed when the service is started.
# At the end of the funtion, a blocking consumer is started
# which listens for new messages.
 # TODO: Setup queues in single place before starting any of the
 # services using RabbitMQ
def main():
    # Setup connection to RabbitMQ service
    connection = establish_connection()
    channel = connection.channel()

    # Declare the exchange that is used for listening
    # and publishing new messages
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    # Declare and bind queue for listening messages with my.o routing key
    channel.queue_declare(queue=IMED_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=IMED_QUEUE, routing_key=CONSUME_ROUTING_KEY)

    # Declare and bind queue for listening messages with my.* wildcard routing key
    # This is done to ensure that the queue for ObseService exists when
    # new messages are posted from this service.
    channel.queue_declare(queue=OBSE_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=OBSE_QUEUE, routing_key=WILDCARD_ROUTING_KEY)

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

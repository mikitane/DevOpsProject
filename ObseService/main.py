# ObseService is responsible for listening
# for messages published with routing key
# that matches my.* wild card key.
# When message is received it is stored to
# the log file

import pika
import time
import os
import requests
from datetime import datetime

# Internal domain name of the RabbitMQ service
BROKER_NAME = 'broker_service'

# Exchange to which all the queues this service uses
# are binded to.
EXCHANGE = 'topic_exchange'

# Handle all messages matching this wild card routing key
ROUTING_KEY = 'my.*'

# Name of the queue that this service uses
OBSE_QUEUE = 'obse_queue'

# Location of the file that is used to store the logs
LOG_FILE_PATH = '/output/logs.txt'


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

# Handler for getting the current state of the application
# from ApiGatewayService.
def get_state():
    state_response = requests.get('http://apigateway_service:8081/state')
    return state_response.content.decode('utf-8')

# Handler for messages published with routing key matching my.*
def on_message(channel, method, properties, body):

    # Save message only in RUNNING state
    if get_state() != 'RUNNING':
        return

    # Generate a log which contains the received message
    # Example: 2020-11-28T12:50:08.524Z Topic my.o: MSG_0
    timestamp = datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + 'Z'
    topic = method.routing_key
    message = body.decode('utf-8')

    log_message = '{timestamp} Topic {topic}: {message}\n'.format(
        timestamp=timestamp,
        topic=topic,
        message=message
    )

    # Save the file to the log file
    f = open(LOG_FILE_PATH, "a")
    f.write(log_message)
    f.close()


# This function is executed when the service is started.
# At the end of the funtion, a blocking consumer is started
# which listens for new messages.
def main():
    # Log file is cleared when the service is started.
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)

    # Setup connection to RabbitMQ service
    connection = establish_connection()
    channel = connection.channel()

    # Declare the exchange that is used for listening for new message
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    # Declare and bind queue for listening messages matching the my.* wildcard key
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

# OrigService is responsible for publishing
# new messages every 3 seconds with my.o routing key
# The service publishes new messages only when the
# application is in RUNNING state

import pika
import time
import requests
from datetime import datetime

# Internal domain name of the RabbitMQ service
BROKER_NAME = 'broker_service'

# Exchange to which all the queues this service uses
# are binded to.
EXCHANGE = 'topic_exchange'

# Publish new messages with this routing key
MY_O_ROUTING_KEY = 'my.o'

# Setup for the queues of ObseService and ImedService
WILDCARD_ROUTING_KEY = 'my.*'
OBSE_QUEUE = 'obse_queue'
IMED_QUEUE = 'imed_queue'


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

# Handler for setting the current state of the application
# through ApiGatewayService.
def set_state(state):
    state_response = requests.put('http://apigateway_service:8081/state', state)
    return state_response.content.decode('utf-8')

# This function is executed when the service is started.
# After setuping the queues it starts to publish new
# messages every 3 seconds if the state of the application is RUNNING
def main():
    # Setup connection to RabbitMQ service
    connection = establish_connection()
    channel = connection.channel()

    # Declare the exchange that is used for listening for new message
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    # Declare and bind queues used by ImedService and ObseService.
    # This is done to ensure that the queues exist when
    # new messages are posted from this service.
    channel.queue_declare(queue=OBSE_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=OBSE_QUEUE, routing_key=WILDCARD_ROUTING_KEY)

    channel.queue_declare(queue=IMED_QUEUE)
    channel.queue_bind(exchange=EXCHANGE, queue=IMED_QUEUE, routing_key=MY_O_ROUTING_KEY)

    # Counts the number of messages sent
    i = 0

    while True:
        # Get the state of the application
        state = get_state()

        # Publish a new message with my.o routing key
        if state == 'RUNNING':
            message = 'MSG_{}'.format(i)

            channel.basic_publish(exchange=EXCHANGE,
                                  routing_key=MY_O_ROUTING_KEY,
                                  body=message)
            i += 1

        # A special state that is used when the application
        # is started or manually set to this state.
        # OrigService notifies other services that
        # it is ready to start sending messages by
        # setting the state to RUNNING
        elif state == 'INIT':
            i = 0
            set_state('RUNNING')

        # Wait 3 seconds before sending a new message
        time.sleep(3)

    connection.close()

# Start the service
main()

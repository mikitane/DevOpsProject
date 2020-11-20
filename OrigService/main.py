import pika
import time
import requests
from datetime import datetime

BROKER_NAME = 'broker_service'
EXCHANGE = 'topic_exchange'
ROUTING_KEY = 'my.o'


def establish_connection(retries=0):
    try:
        return pika.BlockingConnection(pika.ConnectionParameters(BROKER_NAME))
    except pika.exceptions.AMQPConnectionError as e:
        if retries > 10:
            raise e

        time.sleep(2)
        return establish_connection(retries=retries + 1)


def get_state():
    state_response = requests.get('http://apigateway_service:8081/state')
    return state_response.content.decode('utf-8')

def set_state(state):
    state_response = requests.put('http://apigateway_service:8081/state', state)
    return state_response.content.decode('utf-8')

def main():
    print('Starting orig service')
    connection = establish_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    i = 0
    while True:
        state = get_state()

        if state == 'RUNNING':
            message = 'MSG_{}'.format(i)
            print('Sending message with ' + str(i) + 'at: ' + datetime.now().isoformat())

            channel.basic_publish(exchange=EXCHANGE,
                                  routing_key=ROUTING_KEY,
                                  body=message)
            i += 1

        elif state == 'INIT':
            print('Init orig service')

            i = 0
            set_state('RUNNING')

        time.sleep(3)

    connection.close()


# Start the service
main()

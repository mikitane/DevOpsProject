import pika
import time
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

def main():
    connection = establish_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    # FIXME: Setup queues properly, so there is no need to sleep
    # Sleep 3 seconds to ensure other services are ready to receive messages
    time.sleep(3)

    for i in range(1, 4):
        message = 'MSG_{}'.format(i)

        channel.basic_publish(exchange=EXCHANGE,
                            routing_key=ROUTING_KEY,
                            body=message)

        print('Message sent: ', message)
        time.sleep(3)

    connection.close()

# Start the service
main()

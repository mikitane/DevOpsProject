# This file contains all the tests written to test
# the API provided by APIGatewayService.
# APIGatewayService uses other internal services
# to handle the requests.

import unittest
import requests
import json
from time import sleep

# URL from where the API is served
APIGATEWAY_SERVICE_URL = 'http://apigateway_service:8081'

# Helper function for waiting that the application is
# is in certain state.
def wait_for_state(wanted_state):
    for i in range(1, 20):
        state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
        state = state_response.content.decode('utf-8')
        if state == wanted_state:
            return

        sleep(0.5)

    raise Exception('wait_for_state timeout, wanted_state: {}'.format(wanted_state))


class APIGatewayTestCase(unittest.TestCase):

    # Test that RabbitMQ queue statistics are served
    # correctly by StateService
    def test_queue_statistic(self):
        # Ensure that system is in RUNNING state
        wait_for_state('RUNNING')

        expected_keys = {
            'queue',
            'message_delivery_rate',
            'messages_publishing_rate',
            'messages_delivered_recently',
            'message_published_lately'
        }

        # Retry request a few times if not valid.
        # RabbitMQ takes a while before generating first statistics.
        for i in range(1, 5):
            response = requests.get(APIGATEWAY_SERVICE_URL + '/queue-statistic')
            statistics = json.loads(response.content)

            if len(statistics) > 0 and expected_keys == set(statistics[0].keys()):
                break

            sleep(2)

        self.assertEqual(expected_keys, set(statistics[0].keys()))
        self.assertEqual(expected_keys, set(statistics[1].keys()))
        self.assertEqual(2, len(statistics))

    # Test that RabbitMQ node statistics are served
    # correctly by StateService
    def test_node_statistic(self):
        # Ensure that system is in RUNNING state
        wait_for_state('RUNNING')

        expected_keys = {
            'fd_used',
            'disk_free',
            'mem_used',
            'processors',
            'io_read_avg_time',
        }

        # Retry request a few times if not valid.
        # RabbitMQ takes a while before generating first statistics.
        for i in range(1, 5):
            response = requests.get(APIGATEWAY_SERVICE_URL + '/node-statistic')
            statistics = json.loads(response.content)

            if expected_keys == set(statistics.keys()):
                break

            sleep(2)

        self.assertEqual(expected_keys, set(statistics.keys()))

    # Test that logs of the state changes are stored and
    # served correctly by StateService
    def test_run_log(self):
        # Ensure that system is in RUNNING state
        wait_for_state('RUNNING')

        requests.put(APIGATEWAY_SERVICE_URL + '/state', 'PAUSED')
        requests.put(APIGATEWAY_SERVICE_URL + '/state', 'RUNNING')

        response = requests.get(APIGATEWAY_SERVICE_URL + '/run-log')
        logs = response.content.decode('utf-8')

        regex = (
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: INIT\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: RUNNING\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: PAUSED\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: RUNNING\n'
        )

        self.assertRegex(logs, regex)

    # Test that messages are sent and handled correctly
    # by OrigService, ImedService and ObseService
    # Test also that HttpServService serves the message
    # logs correctly
    def test_messages(self):
        # Ensure that system is in RUNNING state
        wait_for_state('RUNNING')

        # Let ORIG service send at least 2 messages.
        # (ORIG has 3 seconds sleep between messages)
        sleep(7)

        response = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages = response.content.decode('utf-8').split('\n')
        messages = [m for m in messages if m]

        for i, message in enumerate(messages):
            # Messages with even index should be sent to
            # topic my.o and with odd index to topic my.i
            message_topic = 'my.o' if i % 2 == 0 else 'my.i'

            # Messages with even index should contain just: MSG_
            # and with odd index should contain: Got MSG_
            message_type = 'MSG_' if i % 2 == 0 else 'Got MSG_'
            message_num = i // 2

            message_regex = 'Topic {}: {}{}'.format(message_topic, message_type, message_num)
            time_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z '
            regex = time_regex + message_regex
            self.assertRegex(message, regex)

    # Test that application generates new messages in RUNNING state.
    def test_state_running(self):
        requests.put(APIGATEWAY_SERVICE_URL + '/state', 'RUNNING')

        messages_response1 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages1_count = messages_response1.content.decode('utf-8').split('\n')

        sleep(5)

        state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages2_count = messages_response2.content.decode('utf-8').split('\n')

        # Ensure state stays RUNNING
        self.assertEqual(state, 'RUNNING')

        # Ensure new messages are sent
        self.assertTrue(messages1_count < messages2_count)

    # Test that no new messages are sent in PAUSED state
    def test_state_paused(self):
        requests.put(APIGATEWAY_SERVICE_URL + '/state', 'PAUSED')

        messages_response1 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages1 = messages_response1.content.decode('utf-8')

        sleep(5)

        state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages2 = messages_response2.content.decode('utf-8')

        # Ensure that state stays PAUSED
        self.assertEqual(state, 'PAUSED')

        # Ensure that no new message are sent in PAUSED state
        self.assertEqual(messages1, messages2)

    # Test that application's data is cleared and that
    # application goes to RUNNING state automatically
    def test_state_init(self):
        requests.put(APIGATEWAY_SERVICE_URL + '/state', 'INIT')

        messages_response = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages = messages_response.content.decode('utf-8')

        self.assertEqual(messages, '')

        sleep(5)

        state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages2_count = len(messages_response2.content.decode('utf-8').split('\n'))

        # Ensure that state is set to RUNNING automatically after INIT
        self.assertEqual(state, 'RUNNING')

        # Ensure that new messages are sent after init
        self.assertTrue(messages2_count > 0)

    # Test that application containers are stopped when
    # state is set to SHUTDOWN
    def test_state_shutdown(self):
        # Wrap with try/except because service shutdown is started immediately.
        # Therefore response might not be delivered.
        try:
            requests.put(APIGATEWAY_SERVICE_URL + '/state', 'SHUTDOWN')
        except:
            pass

        # Poll API until it does not return response
        shutdown = False
        for i in range(1, 20):
            try:
                requests.get(APIGATEWAY_SERVICE_URL + '/state')
                sleep(2)
            except:
                shutdown = True

        self.assertTrue(shutdown)


if __name__ == '__main__':
    unittest.main()

import unittest
import requests
import json
from time import sleep

APIGATEWAY_SERVICE_URL = 'http://apigateway_service:8081'


def wait_for_state(wanted_state):
    for i in range(1, 20):
        state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
        state = state_response.content.decode('utf-8')
        if state == wanted_state:
            return

        sleep(0.5)

    raise Exception('wait_for_state timeout, wanted_state: {}'.format(wanted_state))


class APIGatewayTestCase(unittest.TestCase):
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

    # def test_queue_statistic(self):
    #     # Ensure that system is in RUNNING state
    #     wait_for_state('RUNNING')

    #     response = requests.get(APIGATEWAY_SERVICE_URL + '/queue-statistic')
    #     statistics = json.loads(response.content)

    #     expected_keys = [
    #         'fd_used',
    #         'disk_free',
    #         'mem_used',
    #         'processors',
    #         'io_read_avg_time',
    #     ]

    #     self.assertEqual(expected_keys, list(statistics.keys()))

    # def test_run_log(self):
    #     # Ensure that system is in RUNNING state
    #     wait_for_state('RUNNING')

    #     requests.put(APIGATEWAY_SERVICE_URL + '/state', 'PAUSED')
    #     requests.put(APIGATEWAY_SERVICE_URL + '/state', 'RUNNING')

    #     response = requests.get(APIGATEWAY_SERVICE_URL + '/run-log')
    #     logs = response.content.decode('utf-8')

    #     regex = (
    #         r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: INIT\n'
    #         r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: RUNNING\n'
    #         r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: PAUSED\n'
    #         r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: RUNNING\n'
    #     )

    #     self.assertRegex(logs, regex)

    # def test_messages(self):
    #     # Ensure that system is in RUNNING state and
    #     # let ORIG service send at least 2 messages.
    #     # (ORIG has 3 seconds sleep between messages)
    #     wait_for_state('RUNNING')
    #     sleep(7)

    #     response = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages = response.content.decode('utf-8').split('\n')
    #     messages = [m for m in messages if m]

    #     for i, message in enumerate(messages):
    #         message_topic = 'my.o' if i % 2 == 0 else 'my.i'
    #         message_type = 'MSG_' if i % 2 == 0 else 'Got MSG_'
    #         message_num = i // 2

    #         message_regex = 'Topic {}: {}{}'.format(message_topic, message_type, message_num)
    #         time_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z '
    #         regex = time_regex + message_regex
    #         self.assertRegex(message, regex)

    # def test_state_running(self):
    #     requests.put(APIGATEWAY_SERVICE_URL + '/state', 'RUNNING')

    #     messages_response1 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages1_count = messages_response1.content.decode('utf-8').split('\n')

    #     sleep(5)

    #     state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
    #     state = state_response.content.decode('utf-8')

    #     messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages2_count = messages_response2.content.decode('utf-8').split('\n')

    #     # Ensure state stays RUNNING
    #     self.assertEqual(state, 'RUNNING')

    #     # Ensure new messages are sent
    #     self.assertTrue(messages1_count < messages2_count)

    # def test_state_paused(self):
    #     requests.put(APIGATEWAY_SERVICE_URL + '/state', 'PAUSED')

    #     messages_response1 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages1 = messages_response1.content.decode('utf-8')

    #     sleep(5)

    #     state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
    #     state = state_response.content.decode('utf-8')

    #     messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages2 = messages_response2.content.decode('utf-8')

    #     # Ensure that state stays PAUSED
    #     self.assertEqual(state, 'PAUSED')

    #     # Ensure that no new message are sent in paused state
    #     self.assertEqual(messages1, messages2)

    # def test_state_init(self):
    #     requests.put(APIGATEWAY_SERVICE_URL + '/state', 'INIT')

    #     messages_response = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages = messages_response.content.decode('utf-8')

    #     self.assertEqual(messages, '')

    #     sleep(5)

    #     state_response = requests.get(APIGATEWAY_SERVICE_URL + '/state')
    #     state = state_response.content.decode('utf-8')

    #     messages_response2 = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
    #     messages2_count = len(messages_response2.content.decode('utf-8').split('\n'))

    #     # Ensure that state is set to RUNNING automatically after INIT
    #     self.assertEqual(state, 'RUNNING')

    #     # Ensure that new messages are sent after init
    #     self.assertTrue(messages2_count > 0)

    # def test_state_shutdown(self):
    #     # Wrap with try/except because service shutdown is started immediately.
    #     # Therefore response might not be delivered.
    #     try:
    #         requests.put(APIGATEWAY_SERVICE_URL + '/state', 'SHUTDOWN')
    #     except:
    #         pass

    #     # Poll API until it does not return response
    #     shutdown = False
    #     for i in range(1, 20):
    #         try:
    #             requests.get(APIGATEWAY_SERVICE_URL + '/state')
    #             sleep(2)
    #         except:
    #             shutdown = True

    #     self.assertTrue(shutdown)


if __name__ == '__main__':
    unittest.main()

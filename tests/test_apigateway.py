import unittest
import requests
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
    def test_messages(self):
        # Ensure that system is in RUNNING state and
        # let ORIG service send at least 2 messages.
        # (ORIG has 3 seconds sleep between messages)
        wait_for_state('RUNNING')
        sleep(7)

        response = requests.get(APIGATEWAY_SERVICE_URL + '/messages')
        messages = response.content.decode('utf-8').split('\n')
        messages = [m for m in messages if m]

        for i, message in enumerate(messages):
            message_topic = 'my.o' if i % 2 == 0 else 'my.i'
            message_type = 'MSG_' if i % 2 == 0 else 'Got MSG_'
            message_num = i // 2

            message_regex = 'Topic {}: {}{}'.format(message_topic, message_type, message_num)
            time_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z '
            regex = time_regex + message_regex
            self.assertRegex(message, regex)

        # expected = (
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_1\n'
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_1\n'
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_2\n'
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_2\n'
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_3\n'
        #     r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_3\n'
        # )

        # self.assertRegex(content, expected)

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

        # Ensure that no new message are sent in paused state
        self.assertEqual(messages1, messages2)

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

    def test_state_shutdown(self):
        # Wrap with try/except because service shutdown is started immediately.
        # Therefore response might not be delivered.
        try:
            requests.put(APIGATEWAY_SERVICE_URL + '/state', 'SHUTDOWN')
        except:
            pass

        # Wait for containers to shut down
        #sleep(20)

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


import unittest
import requests
from time import sleep


class APIGatewayTestCase(unittest.TestCase):
    def test_messages(self):
        response = requests.get('http://apigateway_service:8081/messages')
        content = response.content.decode('utf-8')

        expected = (
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_1\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_1\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_2\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_2\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_3\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_3\n'
        )

        self.assertRegex(content, expected)

    def test_state_running(self):
        requests.put('http://apigateway_service:8081/state', data='RUNNING')

        messages_response1 = requests.get('http://apigateway_service:8081/messages')
        messages1_count = messages_response1.content.decode('utf-8').split('\n')

        sleep(5)

        state_response = requests.get('http://apigateway_service:8081/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get('http://apigateway_service:8081/messages')
        messages2_count = messages_response2.content.decode('utf-8').split('\n')

        # Ensure state stays RUNNING
        self.assertEqual(state, 'RUNNING')

        # Ensure new messages are sent
        self.assertTrue(messages1_count < messages2_count)


    def test_state_paused(self):
        requests.put('http://apigateway_service:8081/state', data='PAUSED')

        messages_response1 = requests.get('http://apigateway_service:8081/messages')
        messages1 = messages_response1.content.decode('utf-8')

        sleep(5)

        state_response = requests.get('http://apigateway_service:8081/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get('http://apigateway_service:8081/messages')
        messages2 = messages_response2.content.decode('utf-8')

        # Ensure that state stays PAUSED
        self.assertEqual(state, 'PAUSED')

        # Ensure that no new message are sent in paused state
        self.assertEqual(messages1, messages2)

    def test_state_init(self):
        requests.put('http://apigateway_service:8081/state', data='INIT')

        messages_response = requests.get('http://apigateway_service:8081/messages')
        messages = messages_response.content.decode('utf-8')

        self.assertEqual(messages, 'No content')

        sleep(5)

        state_response = requests.get('http://apigateway_service:8081/state')
        state = state_response.content.decode('utf-8')

        messages_response2 = requests.get('http://apigateway_service:8081/messages')
        messages2_count = len(messages_response2.content.decode('utf-8').split('\n'))

        # Ensure that state is set to RUNNING automatically after INIT
        self.assertEqual(state, 'RUNNING')

        # Ensure that new messages are sent after init
        self.assertTrue(messages2_count > 0)

    def test_state_shutdown(self):
        requests.put('http://apigateway_service:8081/state', data='SHUTDOWN')

        # Services should be unavailable after SHUTDOWN
        with self.assertRaises(Exception):
            requests.get('http://apigateway_service:8081/state')



if __name__ == '__main__':
    unittest.main()


import unittest
import requests


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
        requests.get('http://apigateway_service:8081/state', data='RUNNING')

        messages_response1 = requests.get('http://apigateway_service:8081/messages')
        messages1_count = response1.content.decode('utf-8').split('\n')

        sleep(5)

        state_response = requests.get('http://apigateway_service:8081/state')
        state = response.content.decode('utf-8')

        messages_response2 = requests.get('http://apigateway_service:8081/messages')
        messages2_count = response1.content.decode('utf-8').split('\n')

        self.assertEqual(state, 'RUNNING')

        # Ensure new messages are sent
        self.assertTrue(messages1_count < messages2_count)


    def test_state_paused(self):
        requests.put('http://apigateway_service:8081/state', data='PAUSED')

        messages_response1 = requests.get('http://apigateway_service:8081/messages')
        messages1 = response1.content.decode('utf-8')

        sleep(5)

        state_response = requests.get('http://apigateway_service:8081/state')
        state = response.content.decode('utf-8')

        messages_response2 = requests.get('http://apigateway_service:8081/messages')
        messages2 = response1.content.decode('utf-8')

        self.assertEqual(state, 'PAUSED')

        # Ensure that no new message are sent in paused state
        self.assertEqual(messages1, messages2)

    def test_state_init(self):
        requests.put('http://apigateway_service:8081/state', data='INIT')
        sleep(5)

        response = requests.get('http://apigateway_service:8081/state')
        content = response.content.decode('utf-8')

        self.assertEqual(content, 'RUNNING')


if __name__ == '__main__':
    unittest.main()


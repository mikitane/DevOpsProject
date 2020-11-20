import unittest
import requests


class APIGatewayTestCase(unittest.TestCase):
    def test_messages(self):
        r = requests.get('http://apigateway_service:8081/messages')
        content = r.content.decode('utf-8')

        expected = (
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_1\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_1\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_2\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_2\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.o: MSG_3\n'
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z Topic my\.i: Got MSG_3\n'
        )

        self.assertRegex(content, expected)

if __name__ == '__main__':
    unittest.main()


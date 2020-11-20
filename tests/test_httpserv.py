import unittest
import requests


class TestOutput(unittest.TestCase):
    def test_output(self):
        r = requests.get('http://httpserv_service:8082')
        content = r.content.decode('utf-8')
        print("Test output")
        print(content)
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


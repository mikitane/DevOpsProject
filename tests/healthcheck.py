# Helper script to ensure that APIGatewayService
# is running and ready to receive HTTP requests.

import requests
import time

retries = 0
while True:
	try:
		requests.get('http://apigateway_service:8081')
		break
	except Exception as e:
		if retries > 5:
			raise Exception('Healthcheck failed!')

		time.sleep(2)
		retries += 1

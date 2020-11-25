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

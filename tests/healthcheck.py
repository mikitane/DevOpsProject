import requests
import time

retries = 0
while True:
	print("ASD")

	try:
		requests.get('http://httpserv_service_test:8082')
		print('Healthcheck ok')
		break
	except Exception as e:
		print('Healthcheck failed')
		print(e)
		if retries > 3:
			raise Exception('Healthcheck failed!')

		time.sleep(2)
		retries += 1

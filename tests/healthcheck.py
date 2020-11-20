import requests
import time

retries = 0
while True:
	try:
		requests.get('http://httpserv_service:8082')
		print('Healthcheck ok')
		break
	except Exception as e:
		print('Healthcheck failed')
		print(e)
		if retries > 5:
			raise Exception('Healthcheck failed!')

		time.sleep(2)
		retries += 1

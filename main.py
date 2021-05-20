import requests
import re
import sqlite3

URL = 'https://auto.ria.com/api/search/auto?indexName=auto%2Corder_auto%2Cnewauto_search&price_ot=1&currency=1' \
      '&abroad=2&custom=1&page=0&countpage=20&with_feedback_form=1&withOrderAutoInformer=1&with_last_id=1'
URL_CURRENT_CAR = 'https://auto.ria.com/demo/bu/mainPage/rotator/item/28934898?type=bu&langId=4'
COUNT_PAGES = int(input('Enter count pages:...'))
re_ex = r'\d{8}'
data_cars = []


def get_data_all_cars(ids, url):
	for id_ in ids:
		our_url = url.replace(re.search(re_ex, url).group(0), id_)
		json_data = requests.get(our_url).json()
		print(f'Parse data car with id:{id_}')
		data_cars.append({
			"marka": json_data["marka"],
			"model": json_data["model"],
			"year": json_data["year"],
			"race": json_data["race"],
			"city": json_data["cityLocative"],
			"USD": json_data["USD"],
			"EUR": json_data["EUR"],
			"UAH": json_data["UAH"]
		})
	print('Result:...')
	print(data_cars)


def get_ids_and_pages(url, params=None):
	print('Send get request to url...')
	json_var = requests.get(url, params=params).json()
	ids = []
	if (json_var["result"]["search_result"]["count"]) % 20 == 0:
		num_of_pages = ((json_var["result"]["search_result"]["count"]) // 20) - 1
	else:
		num_of_pages = ((json_var["result"]["search_result"]["count"]) // 20)
	if num_of_pages > 0:
		if COUNT_PAGES < num_of_pages:
			for page in range(COUNT_PAGES):
				print(f'Parse ids on page {page+1}/{COUNT_PAGES}...')
				json_var = requests.get(url, params={'page': page}).json()
				ids.extend(json_var["result"]["search_result"]["ids"])
		else:
			for page in range(num_of_pages + 1):
				print(f'Parse ids on page {page+1}/{COUNT_PAGES}...')
				json_var = requests.get(url, params={'page': page}).json()
				ids.extend(json_var["result"]["search_result"]["ids"])
	else:
		print(f'Parse ids on page 1/{COUNT_PAGES}...')
		ids.extend(json_var["result"]["search_result"]["ids"])
	return ids


get_data_all_cars(get_ids_and_pages(URL), URL_CURRENT_CAR)

import re
import sqlite3 as sq

import requests

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
			"marka": json_data.get("marka", 'Undefined value'),  # dict.get(key, default)
			"model": json_data.get("model", 'Undefined value'),
			"year": json_data.get("year", 'Undefined value'),
			"race": json_data.get("race", 'Undefined value'),
			"city": json_data.get("cityLocative", 'Undefined value'),
			"USD": json_data.get("USD", 'Undefined value').replace(' ', ''),
			"EUR": json_data.get("EUR", 'Undefined value').replace(' ', ''),
			"UAH": json_data.get("UAH", 'Undefined value').replace(' ', ''),
			"id": id_
		})
	print('Result:...')


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
				print(f'Parse ids on page {page + 1}/{COUNT_PAGES}...')
				json_var = requests.get(url).json()
				ids.extend(json_var["result"]["search_result"]["ids"])
				url = url.replace(f'page={page}', f'page={page + 1}')
		else:
			for page in range(num_of_pages + 1):
				print(f'Parse ids on page {page + 1}/{COUNT_PAGES}...')
				json_var = requests.get(url).json()
				ids.extend(json_var["result"]["search_result"]["ids"])
				url = url.replace(f'page={page}', f'page={page + 1}')
	else:
		print(f'Parse ids on page 1/{COUNT_PAGES}...')
		ids.extend(json_var["result"]["search_result"]["ids"])
	return ids


get_data_all_cars(get_ids_and_pages(URL), URL_CURRENT_CAR)

with sq.connect("cars.db") as con:
	cur = con.cursor()

	cur.execute("""
	CREATE TABLE IF NOT EXISTS cars (
	marka TEXT,
	model TEXT,
	year INTEGER,
	race TEXT,
	city TEXT,
	USD INTEGER,
	EUR INTEGER,
	UAH INTEGER,
	ID INTEGER PRIMARY KEY
	)""")
	param = """INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?)"""
	for car in data_cars:
		data_tuple = (car['marka'], car['model'], car['year'], car['race'], car['city'], car['USD'], car['EUR'],
		              car['UAH'], car['id'])
		try:
			cur.execute(param, data_tuple)
		except sq.IntegrityError:
			query = """UPDATE cars SET marka = ?, model = ?, year = ?, race = ?, city = ?, USD = ?, EUR = ?, 
			UAH = ?, id = ? WHERE ID = ?"""
			data_update = (*data_tuple, car['id'])
			cur.execute(query, data_update)
			print(f'Car with id {car["id"]} was update in DB')
	print('The file was create and full')
	con.commit()

import re
import sqlite3 as sq
import datetime
import requests
#from django.utils.dateparse import parse_datetime
URL = 'https://auto.ria.com/api/search/auto?indexName=auto%2Corder_auto%2Cnewauto_search&price_ot=1&currency=1' \
      '&abroad=2&custom=1&page=0&countpage=20&with_feedback_form=1&withOrderAutoInformer=1&with_last_id=1'
URL_CURRENT_CAR = 'https://auto.ria.com/uk/bu/blocks/json/2999/299858/29985840?langId=4&lang_id=4'
COUNT_PAGES = int(input('Enter count pages:...'))
re_ex = r'\d{8}'
data_cars = []


def check_correct_data(lst_dict):
	if lst_dict['autoData'].get('categoryId', 'Undefined value') == 1:
		lst_dict['autoData']['categoryId'] = 'Легкові'
	if lst_dict.get("addDate", 'Undefined value') == 'Undefined value':
		lst_dict["addDate"] = str(datetime.datetime.now())
	if lst_dict['autoData'].get('fuelName', 'Undefined value').strip().isalpha():
		lst_dict['autoData']['fuelName'] = [lst_dict['autoData']['fuelName'], 'Undefined value']
	else:
		lst_dict['autoData']['fuelName'] = lst_dict['autoData']['fuelName'].split(',')


def get_data_all_cars(ids, url):
	for id_ in ids:
		our_url = url.replace(re.search(re_ex, url).group(0), id_)
		json_data = requests.get(our_url).json()
		check_correct_data(json_data)
		print(f'Parse data car with id:{id_}')
		data_cars.append({
			"brand": json_data.get("markName", 'Undefined value').strip(),
			"model": json_data.get("modelName", 'Undefined value').strip(),
			"version": json_data['autoData'].get("version", 'Undefined value').strip(),
			"year": json_data['autoData'].get("year", 'Undefined value'),
			"prise_usd": str(json_data.get("USD", 'Undefined value')).replace(' ', ''),
			"prise_uah": str(json_data.get("UAH", 'Undefined value')).replace(' ', ''),
			"race": json_data['autoData'].get("race", 'Undefined value').strip(),
			"transmission": json_data['autoData'].get("gearboxName", 'Undefined value').strip(),
			"region": json_data['stateData'].get('name', 'Undefined value').strip(),
			"city": json_data.get("cityLocative", 'Undefined value').strip(),
			"engine_type": json_data['autoData'].get("fuelName", 'Undefined value')[0].strip(),
			"engine_capacity": json_data['autoData'].get("fuelName", 'Undefined value')[-1].strip(),
			"plate_number": json_data.get("plateNumber", 'Undefined value').strip(),
			"vin_code": json_data.get("VIN", 'Undefined value').strip(),
			"type_of_transport": json_data['autoData'].get("categoryId", 'Undefined value').strip(),
			"body_type": json_data.get("subCategoryName", 'Undefined value').strip(),
			"drive_type": json_data["autoData"].get("driveName", 'Undefined value').strip(),
			"description": json_data["autoData"].get("description", 'Undefined value'),
			"date_created": json_data.get("addDate", 'Undefined value'),
			"id": id_
		})
	for i in data_cars:
		for j in i:
			print(f'{j}:{i[j]}')
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
		              car['UAH'], int(car['id']))
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

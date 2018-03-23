import argparse
import requests
from bs4 import BeautifulSoup
import requests
import pickle
from time import sleep

base_url = "http://sanctionssearch.ofac.treas.gov/Details.aspx?id={}"


individual_type = "ctl00_MainContent_lblType"
vessel_type = "ctl00_MainContent_lblTypeVessel"
entity_aircraft_type = "ctl00_MainContent_lblTypeOther"


first_name_id = "ctl00_MainContent_lblFirstName"
last_name_id = "ctl00_MainContent_lblLastName"
vessel_name_id = "ctl00_MainContent_lblVesselName"
entity_aircraft_name_id = "ctl00_MainContent_lblNameOther"


error_text = "An error has occured."


tup_list = []

def is_type(soup, match_string):
	match = soup.find(id=match_string)
	return match is not None

def parse_name(soup, match_strings):
	ret = []
	for ms in match_strings:
		match = soup.find(id=ms)
		if match is not None:
			ret.append(match.text)
	return " ".join(ret)

def is_error(soup):
	h4 = soup.findall('h4')
	return error_text in h4[0].text


def scrape(start_num, end_num):
	i = start_num
	while (i < end_num):
		url = base_url.format(i)
		try:
			result = requests.get(url)
			sleep(2)
		except Exception as e:
			sleep(5)
			result = requests.get(url)

		if result.status_code == 200:
			c = result.content
			soup = BeautifulSoup(c, 'lxml')
			
			if is_type(soup, individual_type):
				tup_list.append((parse_name(soup, [first_name_id, last_name_id]), i, "individual"))
			elif is_type(soup, vessel_type):
				tup_list.append((parse_name(soup, [vessel_name_id]), i, "vessel"))
			elif is_type(soup, entity_aircraft_type):
				tup_list.append((parse_name(soup, [entity_aircraft_name_id]), i, "entity/aircraft"))
			elif is_error(soup):
				return
		i += 1
		if i % 100 == 0:
			print(i)




def main():
	start = 0
	end = None
	if args.mode == 'test':	
		end = 20
	elif args.mode == 'initial':
		end = 6216
	elif args.mode == 'update':
		start = 6217
		end = -1


	scrape(start, end)
	
	# with open('ofac_names.txt', 'wb') as f:
	# 	pickle.dump(tup_list, f)




if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Scrape OFAC to build a mapping from name : ofacid')
	parser.add_argument("mode", nargs='?', default="test")
	args = parser.parse_args()

	main()
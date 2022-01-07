from bs4 import BeautifulSoup as bs
import pandas as pd
import requests, json
from random import choice
from get_sale_list import Shoe_data

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		#self.retail_prices, self.shoes_name, self.shoes_urls, self.last_sale, self.volality, self.num_of_sales, self.avg_sale_price  =[],[],[],[],[],[],[]
		self.release_date = []
		self.row_data = []

		self.base_url = "https://stockx.com"
		self.df = pd.read_csv('Items_Data.csv')

		self.headers = self.get_request_params()
		self.brands_urls = self.get_brand_urls()

	def get_shoe_link(self):
		with open('shoes_url_list.txt',"r") as f:
			links = f.readlines()

		shoe_link = links[0][:-1]
		del links[0]

		with open('shoes_url_list.txt',"w") as f:
			f.writelines(links)
		
		return shoe_link

	def get_shoes_data(self):
		data = Shoe_data()

		for i in range(5): # 5 shoes at a time
			shoe_link = self.get_shoe_link()
			res = requests.get(shoe_link, headers=self.headers)
			soup = bs(res.content.decode(), "html.parser")
			print(f"{res} Getting data from: {shoe_link}")

			name = [x.getText() for x in soup.find('h1',{'class':'chakra-heading css-146c51c'})]
			prod_detail = [x for x in soup.find_all('p',{'class':'chakra-text css-imcdqs'})]
			
			try:
				self.shoes_name = [" ".join(name[::len(name) - 1])] #name and color
				self.last_sale = [x.getText().split()[0] for x in soup.find('p',{'class':'chakra-text css-xfmxd4'})]
				data.get_all_data(shoe_link)
			except:
				print(f"Could not get all data from:{res.url}\n")
				with open('err.txt','a') as f:
					f.write(shoe_link + '\n')
				continue	
			
			try:
				self.row_data = [self.shoes_name[0], prod_detail[3].getText(), prod_detail[2].getText()[1:], self.last_sale[0]] #name, releaseDate, retailPrice, lastSale
				self.row_data += [data.history_data[4], None, None, data.history_data[5], data.history_data[7], data.history_data[0], data.history_data[1], data.history_data[2], data.history_data[3]]
			except:
				print("Could not get retail price and or release date\n")
				with open('err.txt','a') as f:
					f.write(shoe_link + '\n')
				continue

			for k in data.size_price_dict:
				self.row_data[5] = k
				self.row_data[6] = data.size_price_dict[k]
			
				df = pd.DataFrame([self.row_data])
				df.to_csv("Items_Data.csv", header=False,index=False, mode='a')

			print(f"done with {self.shoes_name[0]}, Moving on next\n")
		
	def get_max_pages(self, url):
		html_page = requests.get(url, headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return int(soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText())

	def create_shoes_urls_file(self, brand_url):
		max_pages = self.get_max_pages(brand_url)
		
		for page in range(max_pages+1):
			page_url = brand_url + f'?page={page + 1}'
			res = requests.get(page_url, headers=self.headers)
			print(res, page_url)

			soup = bs(res.content.decode(), "html.parser")
			self.shoes_urls += [x.find('a')['href'] for x in soup.find_all('div',{'class':'product-tile css-1trj6wu-TileWrapper'})]

		self.shoes_urls = list(dict.fromkeys(self.shoes_urls))
		
		with open('shoes_url_list.txt','w') as f:
			f.writelines([self.base_url + link + '\n' for link in self.shoes_urls])

	def get_brand_urls(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return [x for x in data['brands_urls'].values()]

	def get_request_params(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return data['headers']

def main():
	crawl = StockX_crawler()

	with open('shoes_url_list.txt') as f:
		file_lines_count = len(f.readlines())

	if(file_lines_count == 0):
		for url in crawl.brands_urls:
			print('\n'+ url)
			crawl.create_shoes_urls_file(url)
	
	with open('shoes_url_list.txt') as f:
		file_lines_count = len(f.readlines())

	for i in range(file_lines_count//5):	
		crawl.get_shoes_data()
		print("finished 5 shoes")

	print("\nFINISHED")
	

if __name__ == "__main__":
	main()

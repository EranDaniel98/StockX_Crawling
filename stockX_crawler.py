from bs4 import BeautifulSoup as bs
import pandas as pd
import requests, json
from random import choice
from get_sale_list import Shoe_data

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		self.retail_prices, self.shoes_name, self.shoes_urls, self.last_sale, self.volality, self.num_of_sales, self.avg_sale_price  =[],[],[],[],[],[],[]
		self.base_url = "https://stockx.com"
		self.df = pd.DataFrame()

		self.headers = self.get_request_params()
		self.brands_urls = self.get_brand_urls()
		
		#for url in self.brands_urls:
		#	print('\n'+ url)
		#	self.get_shoes_urls(url)
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

		for i in range(5):
			shoe_link = self.get_shoe_link()
			res = requests.get(shoe_link, headers=self.headers)
			print(res, shoe_link)
			soup = bs(res.content.decode(), "html.parser")

			name = [x.getText() for x in soup.find('h1',{'class':'chakra-heading css-146c51c'})]
			self.shoes_name += ["".join(name[::len(name) - 1])] #name and color
			print(len(self.shoes_name))

			data.get_all_data(shoe_link)
		
	def get_max_pages(self, url):
		html_page = requests.get(url, headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return int(soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText())

	def get_shoes_urls(self, brand_url):
		max_pages = self.get_max_pages(brand_url)
		f = open('shoes_url_list.txt','w')
		
		for page in range(max_pages+1):
			page_url = brand_url + f'?page={page + 1}'
			res = requests.get(page_url, headers=self.headers)
			print(res, page_url)

			soup = bs(res.content.decode(), "html.parser")
			self.shoes_urls = self.shoes_urls + [x.find('a')['href'] for x in soup.find_all('div',{'class':'product-tile css-1trj6wu-TileWrapper'})]

			f.writelines([self.base_url + link + '\n' for link in self.shoes_urls])
		
		f.close()

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
	crawl.get_shoes_data()
	print("FINISHED")
	

if __name__ == "__main__":
	main()

from os import close
from bs4 import BeautifulSoup as bs
from sklearn.datasets import load_iris
import pandas as pd
import requests
import json

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		self.retail_prices, self.shoes_name, self.shoes_urls, self.last_sale, self.volality, self.num_of_sales  = [],[],[],[],[],[]
		self.base_url = "https://stockx.com/"
		self.df = pd.DataFrame()

		self.headers = self.get_request_params()
		self.brands_urls = self.get_brand_urls()
		
		for url in self.brands_urls:
			print('\n'+ url)
			self.get_shoes_urls(self.brands_urls[0])
		
		self.get_shoes_data()
		
	def get_max_pages(self, url):
		html_page = requests.get(url, headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return int(soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText())
	
	def get_shoes_data(self):
		for i in range(len(self.shoes_urls)):
			res = requests.get(self.base_url + self.shoes_urls[i][1:], headers=self.headers)
			soup = bs(res.content.decode(), "html.parser")

			name = [x.getText() for x in soup.find('h1',{'class':'chakra-heading css-146c51c'})]
			self.shoes_name = self.shoes_name + [" ".join(name[::len(name) - 1])] #name and color

			self.volality = self.volality + [x.getText() for x in soup.find_all('dd',{'class':'chakra-stat__number css-jcr674'})]
			self.retail_prices = self.retail_prices + [x.getText() for x in soup.find_all('p',{'class':'chakra-text css-imcdqs'})]
			self.last_sale = self.last_sale + [x.getText() for x in soup.find_all('p',{'class':'chakra-text css-xfmxd4'})]
		
		print(self.retail_prices)
		self.df['Retail Price'] = pd.Series(self.retail_prices)
		self.df['Shoe Name'] = pd.Series(self.shoes_name)
		self.df['Last Sale'] = pd.Series(self.last_sale)

	def get_shoes_urls(self, brand_url):
		max_pages = self.get_max_pages(brand_url)

		for page in range(max_pages + 1):
			page_url = brand_url + f'?page={page + 1}'
			res = requests.get(page_url, headers=self.headers)
			print(page_url)

			soup = bs(res.content.decode("utf-8"), "html.parser")
			self.shoes_urls = self.shoes_urls + [x.find('a')['href'] for x in soup.find_all('div',{'class':'product-tile css-1trj6wu-TileWrapper'})]

	def get_brand_urls(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return [x for x in data['brands_urls'].values()]

	def get_request_params(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return data['headers']

def main():
	StockX_crawler()

if __name__ == "__main__":
	main()

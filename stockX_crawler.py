from bs4 import BeautifulSoup as bs
from sklearn.datasets import load_iris
import pandas as pd
import requests
import json

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		self.retail_prices, self.shoes_name, self.shoes_urls, self.last_sale,  = [],[],[],[]
		self.base_url = "https://stockx.com/"
		self.df = pd.DataFrame()

		self.headers = self.get_request_params()
		self.brands_urls = self.get_brand_urls()
		
		for url in self.brands_urls:
			print('\n'+ url)
			self.get_shoes_data(url)
		
		#print(len(self.retail_prices), len(self.shoes_name), len(self.shoes_urls))

		
	def get_max_pages(self, url):
		html_page = requests.get(url, headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return int(soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText())

	def get_shoes_data(self, url):
		max_pages = self.get_max_pages(url)

		for page in range(1, 4 + 1):
			page_url = url + f'?page={page}'
			res = requests.get(page_url, headers=self.headers)
			print(page_url)

			soup = bs(res.content.decode("utf-8"), "html.parser")
			self.retail_prices = self.retail_prices + [x.getText() for x in soup.find_all('p',{'class':'chakra-text css-1kph905'})]
			self.shoes_name = self.shoes_name + [x.getText() for x in soup.find_all('p',{'class':'css-1x3b5qq'})]	
			self.shoes_urls = self.shoes_urls + [x.find('a')['href'] for x in soup.find_all('div',{'class':'product-tile css-1trj6wu-TileWrapper'})]
		
		self.df['Retail Price'] = pd.Series(self.retail_prices)
		self.df['Shoe Name'] = pd.Series(self.shoes_name)
		#self.df['Last Sale'] = self.last_sale
		self.df['Links'] = pd.Series(self.shoes_urls)

	def get_brand_urls(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return [x for x in data['brands'].values()]

	def get_request_params(self):
		f = open('crawl_helper.json')
		data = json.load(f)
		return data['headers']

def main():
	StockX_crawler()

if __name__ == "__main__":
	main()

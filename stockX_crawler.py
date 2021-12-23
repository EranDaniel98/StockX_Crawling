from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		self.base_url = "https://stockx.com/"

		self.headers = self.get_params()
		self.get_shoes_data('retro-jordans')
		
	def get_max_pages(self, url):
		html_page = requests.get(url,headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return int(soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText())


	def get_shoes_data(self, brand):
		shoes_prices = []
		shoes_name = []

		shoe_url = self.base_url + brand
		max_pages = self.get_max_pages(shoe_url)

		for page in range(1, 2+1):
			page_url = self.base_url + brand + f'?page={page}'
			res = requests.get(page_url, headers=self.headers)

			soup = bs(res.content.decode("utf-8"), "html.parser")
			shoes_prices = shoes_prices + [x.getText() for x in soup.find_all('p',{'class':'chakra-text css-1kph905'})]
			shoes_name = shoes_name + [x.getText() for x in soup.find_all('p',{'class':'css-1x3b5qq'})]	
			print(res.url)
		
		for i, j in zip(shoes_name, shoes_prices):
			print(i +' - ' + j)
			



	def get_params(self):
		f = open('request_params.json')
		data = json.load(f)
		return data['headers']

def main():
	StockX_crawler()

if __name__ == "__main__":
	main()

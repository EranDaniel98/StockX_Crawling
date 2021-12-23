from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json

from requests.api import head

#python -m json.tool my_json.json

class StockX_crawler:
	def __init__(self):
		self.url = "https://stockx.com/"

		self.headers = self.get_params()
		self.get_shoes_data('retro-jordans')
		
	def get_max_pages(self, url):
		html_page = requests.get(url,headers=self.headers)
		soup = bs(html_page.content.decode("utf-8"), "html.parser")
		return soup.find_all('a',{'class':'css-1sg3yt8-PaginationButton'})[-1].getText()


	def get_shoes_data(self, brand):
		shoe_url = self.url + brand
		max_pages = self.get_max_pages(shoe_url)

		for page in range(1, max_pages+1):
			page_url = self.url + f'?page={page}'
			content = page_url.content.decode("utf-8")
			soup = bs(content, "html.parser")
			shoes_prices = [x.getText() for x in soup.find_all('p',{'class':'chakra-text css-1kph905'})]
			
			print(page_url.url)



	def get_params(self):
		f = open('request_params.json')
		data = json.load(f)
		return data['headers']

def main():
	StockX_crawler()

if __name__ == "__main__":
	main()

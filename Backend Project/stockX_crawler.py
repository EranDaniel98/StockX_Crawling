from os import link
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup as bs
from get_sale_list import Shoe_data
from random import choice


class StockX_crawler:
    def __init__(self):
        self.shoes_urls, self.release_date, self.row_data, self.brands_urls = [], [], [], []

        self.base_url = "https://stockx.com"
        self.df = pd.read_csv('./Backend Project/csv_files/Items_Data.csv')
        self.headers = self.get_request_params()

    def get_shoe_link(self):
        with open('./Backend Project/shoes_url_list.txt', "r") as f:
            links = f.readlines()

        shoe_link = choice(links)  # select ramdom link from the file
        if links.index(shoe_link) == len(links) - 1:
            del links[links.index(shoe_link)]  # Remove that link from list
        else:
            shoe_link = shoe_link[:-1]
            del links[links.index(shoe_link + '\n')]  # Remove that link from list

        # shoe_link = links[0][:-1] #Get the first link from file without the '\n' at the end
        #del links[0]

        with open('./Backend Project/shoes_url_list.txt', "w") as f:
            f.writelines(links)  # Write the new list to the file

        return shoe_link

    def get_shoes_data(self, shoe_link=None):
        data = Shoe_data()

        if shoe_link != None:
            print(f'Getting data from: {shoe_link}')
            data.get_size_count(shoe_link)

            print(f"done with {shoe_link}\n")
            return
        
        else:
            for i in range(5):  # 5 shoes at a time
                shoe_link = self.get_shoe_link()
                print(f'Getting data from: {shoe_link}')
                # Get all the other data that i cant get with request
                data.get_size_count(shoe_link)

                print(f"done with {shoe_link}, Moving on next\n")

    def get_max_pages(self, url):
        html_page = requests.get(url, headers=self.headers)
        soup = bs(html_page.content.decode("utf-8"), "html.parser")
        # Find and return max pages as int
        return int(soup.find_all('a', {'class': 'css-1sg3yt8-PaginationButton'})[-1].getText())

    def create_shoes_urls_file(self, brand_url):
        max_pages = self.get_max_pages(brand_url)  # Get max pages

        for page in range(max_pages + 1):
            # https://stockx.com/brand?page=XXXX
            page_url = brand_url + f'?page={page + 1}'
            res = requests.get(page_url, headers=self.headers)
            print(res, page_url)

            soup = bs(res.content.decode(), "html.parser")
            self.shoes_urls += [x.find('a')['href'] for x in soup.find_all(
                'div', {'class': 'product-tile css-1trj6wu-TileWrapper'})]  # Crawl for shoes links

        # self.shoes_urls = list(dict.fromkeys(self.shoes_urls)) #Remove duplicates

        with open('./Backend Project/shoes_url_list.txt', 'w') as f:
            # Write all links to shoes_url_list.txt
            f.writelines([self.base_url + link + '\n' for link in self.shoes_urls])

    def get_brand_urls(self):
        f = open('./Backend Project/crawl_helper.json')
        data = json.load(f)
        # Return list with all the brands URL's
        return [x for x in data['brands_urls'].values()]

    def get_request_params(self):
        f = open('./Backend Project/crawl_helper.json')
        data = json.load(f)
        return data['headers']

    def get_file_lines_count(self, file):
        with open(file, 'r') as f:
            return len(f.readlines())

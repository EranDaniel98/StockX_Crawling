import requests
import json

class ShoesData():
    def __init__(self):
        self.url = ''
        self.headers = self.get_request_params()


    def get_request_params(self):
        f = open('crawl_helper.json')
        data = json.load(f)
        return data['headers']

    def get_all_sales(self, shoe_url):
        res = requests.get(shoe_url, self.headers)
        data = res.content.decode()

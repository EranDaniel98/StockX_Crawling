from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from bs4 import BeautifulSoup as bs
import time, re, json

class Shoe_data:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

        self.close_popup_script = "document.getElementsByClassName('chakra-modal__close-btn')[0].click()"
        self.close_popup_script2 = "document.getElementsByClassName('chakra-modal__close-btn css-teac1m')[0].click()"
        self.view_sales_script = "document.getElementsByClassName('chakra-button css-2yrtpe')[2].click()"
        self.sales_table_script =  'return document.getElementsByClassName("css-aydg0x")[0].innerHTML'
        self.scroll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.get_historical_data_script = "return document.getElementsByClassName('css-79elbk')[0].innerHTML"
        self.popup_error_msg = 'Could not locate the pop up window/s'

    def get_all_data(self, shoe_url):
        print(shoe_url)
        self.driver.get(shoe_url)
        time.sleep(2)

        try:
            self.driver.execute_script(self.close_popup_script2)
            time.sleep(1)
            self.driver.execute_script(self.close_popup_script)
        except:
            print(self.popup_error_msg)
        
        time.sleep(1)
        
        self.driver.execute_script(self.scroll_down)
        time.sleep(2)
        historical_data = self.driver.execute_script(self.get_historical_data_script)
        time.sleep(2)
        self.parse_historical_data(historical_data)
        
        time.sleep(1)
        self.driver.execute_script(self.view_sales_script)

        time.sleep(2)
        sales_table = self.driver.execute_script(self.sales_table_script)
        self.parse_sales_table(sales_table)

    def parse_sales_table(self, sales_table):
        soup = bs(sales_table,"html.parser")
        
        table = [x.getText() for x in soup.find_all('p',{'class':'chakra-text'})]
        del table[3::5] #remove price tag
        del table[1::4] #remove hour stamp
        table[::3] = [x for x in zip(table[::3],table[2::3])] # Date and price
        del table[2::3] #remove price
        table = table[::-1]

        size_price_dict = {i:[] for i in table[::2]}
        
        # Create dict
        index = 0
        for key in table[::2]:
            size_price_dict[key].append(table[index+1])
            index += 2

        print(len(size_price_dict))

    def parse_historical_data(self, history_data):
        soup = bs(history_data,"html.parser")

        data_root = soup.find('div',{'class':'css-ldihrc'})
        children_data = [x.getText() for x in data_root.findChildren('dd',{'class':'chakra-stat__number css-jcr674'})]
        for i in children_data:
            print(list(map(lambda x: ''.join(x.split(',')),re.findall('([\d,]+)',i))))
    
    def get_login_info(self):
        f = open('crawl_helper.json')
        data = json.load(f)
        return data['login_info']['username'], data['login_info']['password']
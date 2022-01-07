from os import error, spawnle
from pandas._libs.missing import NA
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from bs4 import BeautifulSoup as bs
from time import sleep
import re

class Shoe_data:
    #chakra-modal__close-btn css-1iqbypn 'chakra-modal__close-btn css-1qgkntd'
    close_popup_script = "document.getElementsByClassName('chakra-modal__close-btn css-1iqbypn')[0].click()"
    close_popup_script2 = "document.getElementsByClassName('chakra-modal__close-btn css-1qgkntd')[0].click()"
    view_sales_script = "document.getElementsByClassName('chakra-button css-2yrtpe')[2].click()"
    sales_table_script =  "return document.getElementsByClassName('css-aydg0x')[0].innerHTML"
    scroll_down = "window.scrollTo(0, document.body.scrollHeight)"
    get_historical_data_script = "return document.getElementsByClassName('css-79elbk')[0].innerHTML"

    popup_error_msg = "Could not locate the pop up window/s"
    view_sales_error_msg = "Could not get last sales"
    scroll_down_err = "Could not scroll down"

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

        self.size_price_dict = {}
        self.history_data = []

    def get_all_data(self, shoe_url):
        self.driver.get(shoe_url)
        sleep(2)

        try:
            self.driver.execute_script(self.close_popup_script)
            sleep(2)
            self.driver.execute_script(self.close_popup_script2)
            sleep(1)
        except:
            print(self.popup_error_msg)
            
        try:
            self.driver.find_element_by_xpath("//*[contains(text(),'View Sales')]").click() # View last sales
            sleep(2)

            sales_table = self.driver.find_element_by_class_name('css-aydg0x').get_attribute("innerHTML") # Get last sales HTML and parse it
            self.parse_sales_table(sales_table)
            self.driver.find_element_by_class_name('chakra-modal__close-btn').click() # Close last sales window

        except:
            print(self.view_sales_error_msg)
            return

        sleep(2)
        try:
            self.driver.execute_script(self.scroll_down)
            sleep(1)
            self.driver.execute_script(self.scroll_down)
        
        except:
            print(self.scroll_down_err)
            return

        sleep(4)
        try:
            historical_data = self.driver.find_element_by_class_name('css-79elbk').get_attribute("innerHTML")
            self.parse_historical_data(historical_data)
        
        except:
            print("Unable to locate item in html")
            return


    def parse_sales_table(self, sales_table):
        soup = bs(sales_table,"html.parser")
        
        table = [x.getText() for x in soup.find_all('p',{'class':'chakra-text'})]
        del table[3::5] #remove price tag
        del table[1::4] #remove hour stamp
        del table[::3] #remove date
        table[1::2] = [x[1:] for x in table[1::2]] # remove $ sign

        self.size_price_dict = {}
        self.size_price_dict = {i:[] for i in table[::2]}
        
        # Create dict
        index = 0
        for key in table[::2]:
            self.size_price_dict[key].append(table[index+1])
            index += 2

        for key in self.size_price_dict:
            self.size_price_dict[key] = list(map(lambda s: int(s.replace(',','')), self.size_price_dict[key]))
            self.size_price_dict[key] = sum(self.size_price_dict[key])/ len(self.size_price_dict[key])

    def parse_historical_data(self, history_data):
        self.history_data = []
        soup = bs(history_data,"html.parser")

        data_root = soup.find('div',{'class':'css-ldihrc'})
        children_data = [x.getText() for x in data_root.findChildren('dd',{'class':'chakra-stat__number css-jcr674'})]
        
        self.history_data = list(map(self.fix,self.splitStr(children_data)))
        
        #for i in children_data:
        #   self.history_data.append(''.join(list(map(lambda x: x.replace(',',''), re.findall('(\d[\d,]*)',i)))))

        # min_12, max_12, min_all, max_all, vol, sales, pricePremium, avg_sale_price
    
    def splitStr(self, li):
      res = []
      for i, item in enumerate(li):
        match = re.findall('[\$]*([\d,]+)[\%]*',item)
        if match:
          res += match
        else:
            if i < 2:
                res += ['NaN']*2
            else:
                res += ['NaN']

      return res

    def fix(self, s):
      s =  ''.join([l for l in s.strip() if l.isdigit()])
      return s if s else 'NaN'
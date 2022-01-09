import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from bs4 import BeautifulSoup as bs
from time import sleep

class Shoe_data:
    close_popup_script = "document.getElementsByClassName('chakra-modal__close-btn css-1iqbypn')[0].click()"
    close_popup_script2 = "document.getElementsByClassName('chakra-modal__close-btn css-1qgkntd')[0].click()"
    view_sales_script = "document.getElementsByClassName('chakra-button css-2yrtpe')[2].click()"
    sales_table_script =  "return document.getElementsByClassName('css-aydg0x')[0].innerHTML"
    get_historical_data_script = "return document.getElementsByClassName('css-79elbk')[0].innerHTML"
    scroll_down = "window.scrollTo(0, document.body.scrollHeight)"

    popup_error_msg = "Could not locate the pop up window/s"
    view_sales_error_msg = "Could not get last sales"
    scroll_down_err = "Could not scroll down"

    def __init__(self):
        #chrome_options = Options()
        #chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome()#options=chrome_options)
        self.driver.maximize_window()
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

        self.size_price_dict = {}
        self.history_data = []

    def get_all_data(self, shoe_url):
        self.driver.get(shoe_url)
        sleep(2)

        try: #Try to close the popups
            self.driver.execute_script(self.close_popup_script)
            sleep(3)
            self.driver.execute_script(self.close_popup_script2)
        except:
            print(self.popup_error_msg)
            
        try: #Open last sales view and parse it
            self.driver.find_element_by_xpath("//*[contains(text(),'View Sales')]").click() #View last sales
            sleep(2)

            sales_table = self.driver.find_element_by_class_name('css-aydg0x').get_attribute("innerHTML") #Get last sales HTML
            self.parse_sales_table(sales_table) #parse last sales HTML
            self.driver.find_element_by_class_name('chakra-modal__close-btn').click() #Close last sales window

        except:
            print(self.view_sales_error_msg)
            return

        sleep(2)
        try: #Scroll to the buttom of the page
            self.driver.execute_script(self.scroll_down)
            sleep(2)
            self.driver.execute_script(self.scroll_down)
        
        except:
            print(self.scroll_down_err)
            return

        sleep(2)
        try: #Get historical data and parse it
            historical_data = self.driver.find_element_by_class_name('css-79elbk').get_attribute("innerHTML") #Get the HTML of history table
            self.parse_historical_data(historical_data)
        
        except:
            print("Unable to locate item in html")
            return

    def parse_sales_table(self, sales_table):
        self.size_price_dict = {} #Reset the price dictionary to empty
        
        soup = bs(sales_table, "html.parser")
        table = [x.getText() for x in soup.find_all('p',{'class':'chakra-text'})] #remove excess tags

        del table[3::5] #Remove price tag
        del table[1::4] #Remove hour stamp
        del table[::3] #Remove date
        table[1::2] = [x[1:] for x in table[1::2]] # Remove all $ sign

        self.size_price_dict = {i:[] for i in table[::2]} # Set shoe size as keys and [] as value
        
        index = 0
        for key in table[::2]:
            self.size_price_dict[key].append(table[index+1]) #Append size price to size key
            index += 2 #skip to the next price

        for key in self.size_price_dict: #Fix values in dict
            self.size_price_dict[key] = list(map(lambda s: int(s.replace(',','')), self.size_price_dict[key])) #Parse price string to int, if price is over 999 remove ','
            self.size_price_dict[key] = sum(self.size_price_dict[key])/ len(self.size_price_dict[key]) #Set average price for each key

    def parse_historical_data(self, history_data):
        self.history_data = [] #Reset the list to empty
        soup = bs(history_data, "html.parser")

        data_root = soup.find('div',{'class':'css-ldihrc'}) #Find the root tag for historical data table
        children_data = [x.getText() for x in data_root.findChildren('dd',{'class':'chakra-stat__number css-jcr674'})] #list of all the items in table
        
        self.history_data = list(map(self.fix,self.splitStr(children_data))) #fix values in list - missing vals will be 'None'
    
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
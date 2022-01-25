from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep

class Shoe_data:
    close_popup_script = "document.getElementsByClassName('chakra-modal__close-btn css-1iqbypn')[0].click()"
    close_popup_script2 = "document.getElementsByClassName('chakra-modal__close-btn css-1qgkntd')[0].click()"
    view_sales_script = "document.getElementsByClassName('chakra-button css-2yrtpe')[2].click()"
    sales_table_script = "return document.getElementsByClassName('css-aydg0x')[0].innerHTML"
    get_historical_data_script = "return document.getElementsByClassName('css-79elbk')[0].innerHTML"
    scroll_down_script = "window.scrollTo(0, document.body.scrollHeight);"
    scroll_up_script = 'document.documentElement.scrollTop = 0'

    popup_error_msg = "Could not locate the pop up window/s"
    view_sales_error_msg = "Could not get last sales"
    scroll_down_err = "Could not scroll down"

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

        self.size_price_dict = {}
        self.history_data = []
        self.last_sale, self.shoe_name, self.release_date, self.retail_price = None, None, None, None

    def get_size_count(self, shoe_url):
        self.size_price_dict = {}  # Reset the price dictionary to empty
        self.history_data = []  # Reset the list to empty
        
        self.driver.get(shoe_url)
        sleep(2)
        try:  # Try to close the popups
            self.driver.execute_script(self.close_popup_script)
            sleep(3)
            self.driver.execute_script(self.close_popup_script2)
        except:
            print(self.popup_error_msg)

        try: #Open size chart and get prices
            sleep(3)
            self.driver.find_element_by_id('menu-button-pdp-size-selector').click() #Open size chart
            sleep(2)
            size_count = self.driver.execute_script('return document.getElementsByClassName("chakra-menu__menuitem-option").length') #get the amount of sizes in the chart
            sleep(1)
            self.driver.find_element_by_id('menu-button-pdp-size-selector').click() #Close size chart
            
            self.get_all_data(int(size_count))

        except:
            print('Cant open size chart')

    def get_all_data(self, size_count):
        for i in range(size_count - 4):
            self.driver.find_element_by_id('menu-button-pdp-size-selector').click() #Open size chart
            sleep(2)
            self.select_size(i + 2) #Select size
            sleep(1)
            if self.get_product_details() == 'skip': #Get product details
                return
            sleep(1)
            if self.view_last_sales() == 'empty': #View last sales
                continue 
            self.get_last_sale() #get last sale
            sleep(1)
            self.scroll_down() #scroll down
            sleep(1)
            self.get_historical_data() #get historical data
            sleep(1)

            self.create_row()
            self.scroll_up()
            sleep(2)

    def select_size(self, size):
        try: #Select the size
            self.driver.execute_script(f'document.getElementsByClassName("chakra-menu__menuitem-option")[{size}].click()')
        except:
            print('Couldnt select size')
            return

    def view_last_sales(self):
        try:  # Open last sales view and parse it
            self.driver.find_element_by_xpath("//*[contains(text(),'View Sales')]").click()  # View last sales
            sleep(2)
            
            is_there_sales = self.driver.find_element_by_class_name('css-aydg0x').get_attribute("innerText")
            if 'Nothing to see here' in is_there_sales:
                self.driver.find_element_by_class_name('chakra-modal__close-btn').click()  # Close last sales window
                return 'empty'

            sales_table = self.driver.find_element_by_class_name('css-aydg0x').get_attribute("innerHTML")  # Get last sales HTML
            sleep(1)
            self.driver.find_element_by_class_name('chakra-modal__close-btn').click()  # Close last sales window
            self.parse_sales_table(sales_table)  # parse last sales HTML
    
        except:
            print(self.view_sales_error_msg)
            return

    def get_last_sale(self):
        self.last_sale = self.driver.execute_script('return document.getElementsByClassName("chakra-text css-xfmxd4")[0].innerText')[1:]

    def get_product_details(self):
        try:
            self.shoe_name = self.driver.execute_script('return document.getElementsByClassName("chakra-heading css-146c51c")[0].innerText')
            self.shoe_name = self.shoe_name.replace('\n',' ')

            sleep(2)
            self.retail_price = self.driver.execute_script('return document.getElementsByClassName("chakra-text css-imcdqs")[2].innerText')[1:]
            sleep(2)
            self.release_date = self.driver.execute_script('return document.getElementsByClassName("chakra-text css-imcdqs")[3].innerText')
        except:
            print("Couldnt get retail price or release date")
            return 'skip'

    def scroll_down(self):
        try:  # Scroll to the buttom of the page
            self.driver.execute_script(self.scroll_down_script)
            sleep(2)
            self.driver.execute_script(self.scroll_down_script)

        except:
            print(self.scroll_down_err)
            return
        
    def get_historical_data(self):
        try:  # Get historical data and parse it
            historical_data = self.driver.find_element_by_class_name('css-79elbk').get_attribute("innerHTML")  # Get the HTML of history table
            self.parse_historical_data(historical_data)
        except:
            print("Unable to locate item in html")
            return

    def scroll_up(self):
        try: #Scroll up
            self.driver.execute_script(self.scroll_up_script)
        except: 
            print('Cant scroll up')
            return

    def parse_sales_table(self, sales_table):
        soup = bs(sales_table, "html.parser")
        table = [x.getText() for x in soup.find_all(
            'p', {'class': 'chakra-text'})]  # remove excess tags
        
        if 'Nothing to see here' in table[0]: # No Items
            return

        del table[3::5]  # Remove price tag
        del table[1::4]  # Remove hour stamp
        del table[::3]  # Remove date
        table[1::2] = [x[1:] for x in table[1::2]]  # Remove all $ sign

        # Set shoe size as keys and [] as value
        self.size_price_dict = {i: [] for i in table[::2]}

        index = 0
        for key in table[::2]:
            # Append size price to size key
            self.size_price_dict[key].append(table[index+1])
            index += 2  # skip to the next price

        for key in self.size_price_dict:  # Fix values in dict
            # Parse price string to int, if price is over 999 remove ','
            self.size_price_dict[key] = list(
                map(lambda s: int(s.replace(',', '')), self.size_price_dict[key]))
            self.size_price_dict[key] = sum(self.size_price_dict[key]) / len(
                self.size_price_dict[key])  # Set average price for each key

    def parse_historical_data(self, history_data):
        soup = bs(history_data, "html.parser")

        # Find the root tag for historical data table
        data_root = soup.find('div', {'class': 'css-ldihrc'})
        children_data = [x.getText() for x in data_root.findChildren(
            'dd', {'class': 'chakra-stat__number css-jcr674'})]  # list of all the items in table

        # fix values in list - missing vals will be 'None'
        self.history_data = self.fix_history_data_items(children_data)

    def fix_history_data_items(self, history_list):
        history_list = [i.split() for i in history_list]

        res = []
        for i in history_list:
            for j in i:
                j = j.replace('$', '')
                j = j.replace('%', '')
                j = j.replace(',', '')
                j = j.replace('--', 'NaN')
                if j != '-':
                    res.append(j)
        return res

    def clean_var(self):
        self.last_sale = self.shoe_name = self.release_date = self.retail_price = self.history_data = []
        self.size_price_dict = {}

    def create_row(self):
        row = [self.shoe_name, self.release_date, self.retail_price, self.last_sale]
        # Volality, size, avg price size, number of sales, price premium, avg sale price, min range
        row += [self.history_data[4],None, None, self.history_data[5], self.history_data[6], self.history_data[7], self.history_data[0], self.history_data[1], self.history_data[2], self.history_data[3]]

        for k in self.size_price_dict:
            row[5] = k
            row[6] = self.size_price_dict[k]
			
        print(row)
        
        df = pd.DataFrame([row])
        df.to_csv("./csv_files/Items_Data.csv", header=False,index=False, mode='a')
        self.clean_var()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from bs4 import BeautifulSoup as bs
import time, os

class Shoe_data:
    def __init__(self, shoe_url):
        self.shoe_url = shoe_url

        self.driver = webdriver.Chrome()
        stealth(self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

        self.sales_table_script =  'return document.getElementsByClassName("css-aydg0x")[0].innerHTML'
        self.parse_sales_table()

    def get_all_sales(self):
        self.driver.get(self.shoe_url)
        time.sleep(5)

        try:
            self.driver.execute_script("document.getElementsByClassName('chakra-modal__close-btn')[0].click()")
            time.sleep(1)
            self.driver.execute_script("document.getElementsByClassName('chakra-modal__close-btn')[0].click()")
        except:
            print("Could not locate the pop up window/s")
            
        time.sleep(1)
        self.driver.execute_script("document.getElementsByClassName('chakra-button css-2yrtpe')[2].click()")
        time.sleep(5)

        return self.driver.execute_script(self.sales_table_script)

    def parse_sales_table(self):
        sales_table = self.get_all_sales()
        soup = bs(sales_table,"html.parser")
        
        table = [x.getText() for x in soup.find_all('p',{'class':'chakra-text'})]
        del table[3::5] #remove price tag
        #print(table)
        del table[1::4] #remove hour stamp
        table[::3] = [x for x in zip(table[::3],table[2::3])] # Date
        del table[2::3]
        table = table[::-1]

        res = {}
        for i in table[::2]:
            res[i] = []

        index = 0
        for key in table[::2]:
            res[key].append(table[index+1])
            index += 2

        print(res['10.5'])            
        

def main():
    Shoe_data('https://stockx.com/air-jordan-11-retro-cool-grey-2021')

if __name__ == "__main__":
	main()
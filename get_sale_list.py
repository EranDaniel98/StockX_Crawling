from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from bs4 import BeautifulSoup as bs
import time, os

class Shoe_data:
    def __init__(self, shoe_url):
        self.shoe_url = shoe_url

        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36" 
        sec_ch_ua = '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"' 
        referer = "https://www.google.com"
        options = webdriver.ChromeOptions() 
        options.headless = True 

        def interceptor(request): 
            del request.headers["user-agent"] # Delete the header first 
            request.headers["Host"] = "stockx.com"
            request.headers["user-agent"] = user_agent 
            request.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            request.headers["Accept-Language"] = "en-GB,en;q=0.5"
            request.headers["Accept-Encoding"] = "gzip, deflate, br"
            request.headers["Connection"] = "keep-alive"
            request.headers["Cookie"] = "stockx_homepage=sneakers; stockx_experiments_id=web-5234ce40-74bf-4383-8e75-d450b203286f; stockx_market_country=SG; hide_my_vices=false; stockx_session=%22ab76089a-6183-43cf-9b97-948a86689ec7%22; forterToken=cf8feedd3cd140f7aceb603f2be6a125_1640263352107_306_dUAL43-mnts-ants_13ck; _dd_s=rum=0&expire=1640264352964; ab_one_buy_now_v2_button=true; stockx_preferred_market_activity=sales; _px_7125205957_cs=eyJpZCI6ImMyNjU3MjMwLTYzZWQtMTFlYy1iMDNkLTkxZjEzZTQ5MGI1MSIsInN0b3JhZ2UiOnt9LCJleHBpcmF0aW9uIjoxNjQwMjY1MjYxMjU0fQ==; _px_f394gi7Fvmc43dfg_user_id=YzI2NTk5NDEtNjNlZC0xMWVjLWIwM2QtOTFmMTNlNDkwYjUx; _ga=undefined; stockx_selected_currency=SGD; language_code=en; stockx_selected_locale=en; stockx_selected_region=SG; stockx_dismiss_modal=true; stockx_dismiss_modal_set=2021-12-23T12%3A42%3A17.871Z; stockx_dismiss_modal_expiration=2022-12-23T12%3A42%3A17.871Z"
            request.headers["Upgrade-Insecure-Requests"] = "1"
            request.headers["Sec-Fetch-Dest"] = "document"
            request.headers["Sec-Fetch-Mode"] = "navigate"
            request.headers["Sec-Fetch-Site"] = "none"
            request.headers["Sec-Fetch-User"] = "?1"
            request.headers["TE"] = "trailers"

        with webdriver.Chrome(options=options) as self.driver:
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
        self.driver.execute_script("document.getElementsByClassName('chakra-button css-2yrtpe')[1].click()")
        time.sleep(5)

        return self.driver.execute_script(self.sales_table_script)

    def parse_sales_table(self):
        sales_table = self.get_all_sales()
        soup = bs(sales_table,"html.parser")
        sizes = [x.getText() for x in soup.find_all('p',{'class':'hakra-text'})]
        

def main():
    Shoe_data('https://stockx.com/air-jordan-11-retro-cool-grey-2021')

if __name__ == "__main__":
	main()
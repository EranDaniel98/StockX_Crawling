from stockX_crawler import StockX_crawler
from prediction import predict
import pandas as pd
import os.path

from sub_predict import sub_predict

class main_class:
    def __init__(self,url):
        main(url)


def main(url=None):
    crawl = StockX_crawler()
    if url != None:
        shoe_url = url
        pred = predict('.//csv_files/Items_Data.csv')
        sub_pred = sub_predict(pred)

        if sub_pred.predict_shoe_price(shoe_url) == 'shoe not found':
            # scrape all the data from the site and use predict again!
            crawl.get_shoes_data(shoe_url)
            sort_csv()
            pred = predict('.//csv_files/Items_Data.csv')
            handle_procc_df_csv(pred=pred)
            sub_pred = sub_predict(pred)
            sub_pred.predict_shoe_price(shoe_url)
    else:
        # Every other run:
        if(input('Is it first run? Y/N ').lower() == 'y'):
        # First time run:
            pred = predict()

            if os.path.isfile('./csv_files/Items_Data.csv') == False:
                create_shoes_url_file(crawl)
                crawl_shoes_data(crawl)
                sort_csv()

            if os.path.isfile('.//csv_files/proccessed_dataframe.csv') == False:
                handle_procc_df_csv(pred=pred)
        
    
    print('FINISHED')

def handle_procc_df_csv(df=None, pred=None):
    if pred == None:
        pred = predict(df)

    pred.replace_price_premium()
    pred.df = pred.df.drop_duplicates()
    pred.df = pred.df.dropna(how='any', axis=0)
    pred.parse_date_to_days_diff()
    pred.fix_data()

def create_shoes_url_file(crawl):
    file_lines_count = crawl.get_file_lines_count('.//txt_files/shoes_url_list.txt')

    if(file_lines_count == 0):  # If there are no shoes links in 'shoes_link_url.txt'
        crawl.brands_urls = crawl.get_brand_urls()  # crawl for shoes links

        for url in crawl.brands_urls:
            print('\n' + url)
            crawl.create_shoes_urls_file(url)

def crawl_shoes_data(crawl):
    file_lines_count = crawl.get_file_lines_count('.//txt_files/shoes_url_list.txt')  # get shoes link len

    while(file_lines_count != 0):
        crawl.get_shoes_data()
        file_lines_count = crawl.get_file_lines_count('.//txt_files/shoes_url_list.txt')

        print('Finished 5 shoes')

def sort_csv():
    df = pd.read_csv('.//csv_files/Items_Data.csv')
    df.sort_values(by=['shoes_name'])
    df.to_csv('.//csv_files/Items_Data.csv', index=False)

def print_models_score(pred):
    print("Random Forest res: ", pred.random_forest(pred.df))
    print("Decision Tree res: ", pred.dec_tree(pred.df))
    print("GB res: ", pred.gb(pred.df))
    print("Liniar res: ", pred.linear(pred.df))

if __name__ == "__main__":
    try:
        with open('.//txt_files/requestedURL.txt','r') as f:
            url = f.readline()
            main(url)
    except:
        main()

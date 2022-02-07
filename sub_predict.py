from stockX_crawler import StockX_crawler
import pandas as pd
import warnings
import re

warnings.filterwarnings("ignore")


class sub_predict:

    def __init__(self, pred):
        self.pred = pred
        self.df = pd.read_csv('./csv_files/proccessed_dataframe.csv')
    
    def search_shoe(self, shoe_url):
        df = pd.read_csv('./csv_files/half_procc_df.csv')
        
        shoe_name = shoe_url[shoe_url.rfind('/')+1:].replace('-',' ').replace('air ','')
        
        df['shoes_name'] = df['shoes_name'].str.lower()
        lines = df.index[df['shoes_name'].str.contains(shoe_name)].tolist()
        
        if lines == []:        
            shoe_name = re.sub(r'[0-9]','',shoe_name).lower()
            lines = df.index[df['shoes_name'].str.contains(shoe_name)].tolist()
        
        return lines

    def predict_shoe_price(self, shoe_url):
        shoe_df_location = self.search_shoe(shoe_url)
        if shoe_df_location != []:
            shoe_df = self.df.iloc[shoe_df_location]
            #print(shoe_df)
            shoe_df = shoe_df.drop(['last_sale', 'min_all_trade_range', 'max_all_trade_range'], axis=1)
            
            data = []
            predicted_prices = []

            print("Predicting...", end='')
            for i in range(len(shoe_df_location)):
                print(f'...',end='')
                data += [[x for x in shoe_df.iloc[i]]]
                predicted_prices.append(self.pred.new_item_predict(self.df, data)[0])
            
            print('\n')
            for i, size in enumerate(shoe_df['shoe_size']):
                print(f"shoe size: {size}, shoe price: {predicted_prices[i]}")

        else:
            print("The shoe is not in the dataframe")
            return 'shoe not found'
            
    def fix_half_procc_shoes_name(self, shoe_names):
        new_names = " ".join(re.sub(r'[^\w]', ' ',shoe_names.str.lower()).split())
        
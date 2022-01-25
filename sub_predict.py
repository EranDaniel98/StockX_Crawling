from multiprocessing.dummy import Array
import pandas as pd
from prediction import predict
import warnings

warnings.filterwarnings("ignore")

class sub_predict:

    def __init__(self, pred):
        self.pred = pred
        self.df = pred.df
    
    def search_shoe(self, shoe_url):
        df = pd.read_csv('./csv_files/half_procc_df.csv')

        shoe_name = shoe_url[shoe_url.rfind('/')+1:].replace('-',' ')
        lines = df.index[df['shoes_name'].str.lower() == shoe_name].tolist()
        return lines

    def predict_shoe_price(self, shoe_url):
        df = pd.read_csv('./csv_files/proccessed_dataframe.csv')

        shoe_df_location = self.search_shoe(shoe_url)
        if shoe_df_location != []:
            shoe_df = df.iloc[shoe_df_location]
            #print(shoe_df)
            shoe_df = shoe_df.drop(['last_sale', 'min_all_trade_range', 'max_all_trade_range'], axis=1)
            
            data = []
            predicted_prices = []

            for i in range(len(shoe_df_location)):
                print("Predicting...")
                data += [[x for x in shoe_df.iloc[i]]]
                predicted_prices.append(self.pred.new_item_predict(df, data)[0])
            
            for i, size in enumerate(shoe_df['shoe_size']):
                print(f"shoe size: {size}, shoe price: {predicted_prices[i]}")

        else:
            print("SHOE NOT FOUND")
            # scrape all the data from the site and use predict again!
            return
        
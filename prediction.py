# %%
import pandas as pd
import numpy as np
import os , sklearn 
import datetime
from sklearn import preprocessing, linear_model, model_selection
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression

# %%
class predict:
    def __init__(self):
        self.df = self.get_dataframe()
        self.df = self.df.dropna(how='any',axis=0)
        self.df.drop_duplicates()
        
    def get_dataframe(self):    
        with open('Items_Data.csv','r') as f:
            return pd.read_csv(f)
    
    def int_parse_release_date(self):
        shoe_dates = self.df['release_date']
        todays_date = datetime.datetime.today()
        
        index = 0
        for date in shoe_dates:
            format = '%d/%m/%Y'
            fix_date = datetime.datetime.strptime(date, format)
            diff = todays_date - fix_date
            
            self.df['release_date'].iloc[index] = diff.days
            index = index + 1
    
# %%
pred = predict()
pred.int_parse_release_date()
print(pred.df['release_date'])


# %%

# %%
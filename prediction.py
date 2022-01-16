#%%
from sklearn import linear_model, tree, ensemble
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import datetime, re
import pandas as pd
import numpy as np
# %%

class predict:
######################################################### cleaning data  ###############################################################

    def __init__(self):
        self.df = self.get_dataframe()
        self.df = self.df.drop('avg_size_price', axis = 1)
        self.df = self.df.replace('', np.nan)

    def get_dataframe(self):    
        return pd.read_csv('Items_Data.csv')

    def replace_price_premium(self): # Calc the price premium by formula and replace the current values
        retail_prices = self.df['retail_price']
        avg_sale_prices = self.df['avg_sale_price']
        df_length = len(self.df['price_premium'])

        for i in range(df_length):
           self.df['price_premium'].iloc[i] = ((avg_sale_prices[i] - retail_prices[i])/retail_prices[i])  * 100
           #keep only 2 numbers after decimal
           #self.df['price_premium'].iloc[i] = '%.2f' % self.df['price_premium'].iloc[i]

######################################################### data fixing  #################################################################
    
    def parse_date_to_days_diff(self):
        #change dates from dd/mm/yyyy to days diff
        shoe_dates = self.df['release_date']
        todays_date = datetime.datetime.today() #format - y m d
        format = '%d/%m/%Y'
        
        for index, date in enumerate(shoe_dates):
            shoe_date = datetime.datetime.strptime(date, format)
            diff = todays_date - shoe_date
            self.df['release_date'].iloc[index] = diff.days

    def fix_data(self):
        for i in range(len(self.df)):
            self.df['shoe_size'].iloc[i] = ''.join(re.findall('^[\d.\d]+',self.df['shoe_size'].iloc[i])) #keeps only numbers
            self.df['last_sale'].iloc[i] = ''.join(re.findall('^[\d.\d]+',self.df['last_sale'].iloc[i])) #keeps only numbers
        
        self.df = self.df.replace('', np.nan)
        self.df = self.df.dropna(how='any',axis=0)
        
        self.df['shoe_size'] = pd.Series(map(float, self.df['shoe_size']))
        self.df['last_sale'] = pd.Series(map(float, self.df['last_sale'])) 

        #turn unique names into numerics 
        self.df['shoes_name'], trash = pd.factorize(self.df['shoes_name']) 

 
######################################################### Check Correlation  ###########################################################

    def get_correlation(self):
        df_copy = self.df.copy()
        
        col_1 = df_copy['last_sale']
        df_copy = df_copy.drop('last_sale', axis=1)

        corr_res = []
        for col in df_copy.columns:
            corr_res.append((col, col_1.corr(df_copy[col])))
        
        self.draw_corr_plot()
        
        
        #corr_res.sort(key=lambda x: x[1], reverse=True)
        #cols = [x[0] for x in corr_res][:4]
        #self.draw_scatter_plot('last_sale', cols)
    
    def draw_scatter_plot(self, master_col, cols):
        fig, axes = plt.subplots(4,1, figsize=(20,20))
        axe = axes.ravel()
        
        for i, col in enumerate(cols):
            scatter_df = self.df[[master_col, col]]
            sns.scatterplot(data=scatter_df, ax=axe[i])

    def draw_corr_plot(self):
        f = plt.figure(figsize=(20, 20))
        plt.matshow(self.df.corr(), fignum=f.number)
        plt.xticks(range(self.df.select_dtypes(['number']).shape[1]), self.df.select_dtypes(['number']).columns, fontsize=16, rotation=45)
        plt.yticks(range(self.df.select_dtypes(['number']).shape[1]), self.df.select_dtypes(['number']).columns, fontsize=16)
        cb = plt.colorbar()
        cb.ax.tick_params(labelsize=20)
        plt.title('Correlation Matrix', fontsize=24)

######################################################### Check permutations  ##########################################################

    def check_premutations(self): #helps to understand what columns have most impact on the model
        X_train, X_test, y_train, y_test = self.split_model()
        model = tree.DecisionTreeRegressor(max_depth=5).fit(X_train,y_train)
        model.score(X_test, y_test)

        r = permutation_importance(model,X_test,y_test, n_repeats=30, random_state=0)

        for i in r.importances_mean.argsort()[::-1]:
            if(r.importances_mean[i] -2 * r.importances_std[i] > 0):
               print(f"{model.feature_names_in_[i]:<8}"
                     f" {r.importances_mean[i]:.3f}"
                     f" +/- {r.importances_std[i]:.3f}")

######################################################### Model Training  ##############################################################      

    def split_model(self):
        df_copy = self.df.copy()
        y = df_copy[['last_sale']]
        X = df_copy.drop(['last_sale','max_all_trade_range','min_all_trade_range'], axis = 1)

        df_copy.to_csv('proccessed_dataframe.csv', index=False)
        
        return train_test_split(X,y, random_state=0)

    def dec_tree(self):
        X_train, X_test, y_train, y_test = self.split_model()#split to train and test
        
        model = tree.DecisionTreeRegressor(max_depth=5)#build
        model.fit(X_train, y_train) #train
        model.score(X_test, y_test) #make predition
        
        y_pred = model.predict(X_test)
        print(r2_score(y_test,y_pred))
        print(model.feature_importances_)

    def random_forest(self):
        X_train, X_test, y_train, y_test = self.split_model()

        model = ensemble.RandomForestRegressor(n_estimators=100)
        model.fit(X_train, np.ravel(y_train))
        model.score(X_test, y_test)
        y_pred = model.predict(X_test)

        print(r2_score(y_test,y_pred))
        print(model.feature_importances_)
        
    def gb(self):
        X_train, X_test, y_train, y_test = self.split_model()

        model = ensemble.GradientBoostingRegressor(n_estimators=40)
        model.fit(X_train, y_train)
        model.score(X_test, y_test)

        y_pred = model.predict(X_test)
        
        print(r2_score(y_test,y_pred))
        print(model.feature_importances_)

    def linear(self):
        X_train, X_test, y_train, y_test = self.split_model()
        
        model = linear_model.LinearRegression()
        model = model.fit(X_train, y_train)
        model.score(X_test, y_test)
        
        y_pred = model.predict(X_test)

        print(r2_score(y_test,y_pred))
        print(model.feature_importances_)
# %%
######################################################### END OF CLASS  ################################################################
#%%
def fix_dates():

    with open('project dates/all_dates.txt') as f:
        all_dates = f.readlines()
    
    with open('project dates/bad_dates.txt') as f:
        bad_dates = f.readlines()
    
    with open('project dates/fixed_bad_dates.txt') as f:
        fixed_bad_dates = f.readlines()
    
    k = 0
    for i in bad_dates:
        if i in all_dates:
            all_dates[all_dates.index(i)] = fixed_bad_dates[k]
            k += 1 
    
    with open('fixed_dates.txt','w') as f:
        f.writelines(all_dates)
#%%
def main():

    pred = predict()
    pred.replace_price_premium()

    pred.df = pred.df.drop_duplicates()
    pred.df = pred.df.dropna(how='any', axis=0)

    pred.parse_date_to_days_diff()
    pred.fix_data()
    #pred.get_correlation()
    print("Random Forest res: ", pred.random_forest())
    #print("Dec tree res: ", pred.dec_tree())
    #print("gb es: ", pred.gb())
    return


if __name__ == '__main__':
    main()

# %%

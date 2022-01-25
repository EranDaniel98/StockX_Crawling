from sklearn import linear_model, tree, ensemble
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import datetime, re
import pandas as pd
import numpy as np


class predict:
######################################################### cleaning data  ###############################################################

    def __init__(self, processed_df=None):
        self.random_forest_model = ensemble.RandomForestRegressor(n_estimators=100)
        self.dec_tree_model = tree.DecisionTreeRegressor(max_depth=5)
        self.liniar_model = None
        self.gb_model = None
        
        if processed_df is None:
            self.factorize_dict = {}
            self.df = self.get_dataframe()
            self.df = self.df.drop('avg_size_price', axis = 1)
            self.df = self.df.replace('', np.nan)
        else:
            self.df = pd.read_csv(processed_df)

    def get_dataframe(self):    
        return pd.read_csv('./csv_files/Items_Data.csv')

    def replace_price_premium(self): # Calc the price premium by formula and replace the current values
        retail_prices = self.df['retail_price']
        avg_sale_prices = self.df['avg_sale_price']
        df_length = len(self.df['price_premium'])

        for i in range(df_length):
           self.df['price_premium'].iloc[i] = ((avg_sale_prices[i] - retail_prices[i])/retail_prices[i])  * 100
           #keep only 2 numbers after decimal
           self.df['price_premium'].iloc[i] = '%.2f' % self.df['price_premium'].iloc[i]

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
        
        #self.df['shoe_size'] = pd.Series(map(float, self.df['shoe_size']))
        #self.df['last_sale'] = pd.Series(map(float, self.df['last_sale'])) 

        #turn unique names into numerics 
        self.df.sort_values(by=['shoes_name'])
        self.df.to_csv('half_procc_df.csv', index=False)
        self.factorize_2()
        self.df.to_csv('proccessed_dataframe.csv', index=False)
    
    def factorize_2(self):
        unique_vals = self.df['shoes_name'].unique()
        print(len(unique_vals))
        #Setting up the dict
        for i in unique_vals:
            self.factorize_dict[i] = 0

        i = 0
        for val in self.df['shoes_name']:
            if self.factorize_dict[val] == 0:
                self.factorize_dict[val] = i
                i += 1

        for i in range(len(self.df['shoes_name'])):
            self.df['shoes_name'].iloc[i] = self.factorize_dict[self.df['shoes_name'].iloc[i]]
        
        self.df.to_csv('proccessed_dataframe.csv', index=False)
        self.df = pd.read_csv('./csv_files/proccessed_dataframe.csv')

######################################################### Check Correlation  ###########################################################

    def get_correlation(self):
        df_copy = self.df.copy()
        
        col_1 = df_copy['last_sale']
        df_copy = df_copy.drop('last_sale', axis=1)

        corr_res = []
        for col in df_copy.columns:
            print(col_1.corr(df_copy[col]))
            corr_res.append((col, col_1.corr(df_copy[col])))
        
        #self.draw_corr_plot()
        
        corr_res.sort(key=lambda x: x[1], reverse=True)
        cols = [x[0] for x in corr_res][:4]
        self.draw_scatter_plot('last_sale', cols)
    
    def draw_scatter_plot(self, master_col, cols):
        fig, axes = plt.subplots(4,1, figsize=(20,20))
        axe = axes.ravel()
        #print(cols)
        
        for i, col in enumerate(cols):
            scatter_df = self.df[[master_col, col]]
            ax = sns.scatterplot(data=scatter_df[:100], ax=axe[i])
            ax.set_xlabel('Shoes Index',size=20)
            ax.set_ylabel('Value',size=20)
            ax.set_title(f'\"{master_col}\" & \"{col}\" correlation', size=24)
            plt.subplots_adjust(hspace=0.6)
        
        plt.savefig('./plots/retailPrice_corr.png',bbox_inches="tight")
            
    def draw_corr_plot(self):
        corr_mat = self.df.corr()
        columns = self.df.columns

        f, ax = plt.subplots(figsize=(25,25))

        heatmap = sns.heatmap(corr_mat,square=True, linewidths=.5, cmap='coolwarm',cbar_kws =
        {'shrink': .4,'ticks' : [-1, -.5, 0, 0.5, 1]},
        vmin = -1,
        vmax = 1,
        annot = True,
        annot_kws = {"size": 22})
        
        ax.set_yticklabels(corr_mat.columns, rotation = 0, size=23)
        ax.set_xticklabels(corr_mat.columns, size=23)
        ax.set_title('Correlation Matrix', fontsize=32)
        sns.set_style({'xtick.bottom':True},{'ytick.left':True})

        plt.savefig('./plots/corr_matrix.png',bbox_inches="tight")

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

    def split_model(self, train_df):
        df_copy = train_df.copy()
        y = df_copy[['last_sale']]
        X = df_copy.drop(['last_sale','max_all_trade_range','min_all_trade_range'], axis = 1)
        
        return train_test_split(X,y, random_state=0)

    def dec_tree(self, df):
        X_train, X_test, y_train, y_test = self.split_model(df)#split to train and test
        
        self.dec_tree_model.fit(X_train, np.ravel(y_train)) #train
        #model.score(X_test, y_test) #make predition
        self.dec_tree_model = self.dec_tree_model

        y_pred = self.dec_tree_model.predict(X_test)
        return r2_score(y_test,y_pred)
    
    def random_forest(self,train_df):
        X_train, X_test, y_train, y_test = self.split_model(train_df)

        self.random_forest_model.fit(X_train, np.ravel(y_train)) #train
        y_pred = self.random_forest_model.predict(X_test)

        return r2_score(y_test,y_pred)
        
    def gb(self,df):
        X_train, X_test, y_train, y_test = self.split_model(df)

        model = ensemble.GradientBoostingRegressor(n_estimators=40)
        model.fit(X_train, np.ravel(y_train)) #train
        model.score(X_test, y_test)

        y_pred = model.predict(X_test)
        
        #print(model.feature_importances_)
        return r2_score(y_test,y_pred)

    def linear(self,df):
        X_train, X_test, y_train, y_test = self.split_model(df)
        
        model = linear_model.LinearRegression()
        model.fit(X_train, np.ravel(y_train)) #train
        model.score(X_test, y_test)
        
        y_pred = model.predict(X_test)

        #print(model.feature_importances_)
        return r2_score(y_test,y_pred)

    def new_item_predict(self, df, pred_col):
        X_train, X_test, y_train, y_test = self.split_model(df)
        self.random_forest_model.fit(X_train, np.ravel(y_train)) #train
        # self.dec_tree_model.fit(X_train, np.ravel(y_train))
        # 3rd model
        # 4th model

        rf_y_pred = self.random_forest_model.predict(pred_col)
        #_y_pred = self.dec_tree_model.predict(pred_col)
        #_y_pred = self.random_forest_model.predict(pred_col)
        #_y_pred = self.random_forest_model.predict(pred_col)
        return rf_y_pred

######################################################### END OF CLASS  ################################################################
def fix_dates():

    with open('project_dates/all_dates.txt') as f:
        all_dates = f.readlines()
    
    with open('project_dates/bad_dates.txt') as f:
        bad_dates = f.readlines()
    
    with open('project_dates/fixed_bad_dates.txt') as f:
        fixed_bad_dates = f.readlines()
    
    k = 0
    for i in bad_dates:
        if i in all_dates:
            all_dates[all_dates.index(i)] = fixed_bad_dates[k]
            k += 1 
    
    with open('fixed_dates.txt','w') as f:
        f.writelines(all_dates)
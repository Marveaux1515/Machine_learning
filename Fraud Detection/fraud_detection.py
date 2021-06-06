# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 15:54:15 2020

@author: Administrator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split,GridSearchCV,StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix,precision_score,recall_score,f1_score,roc_auc_score
from sklearn.decomposition import PCA
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.svm import LinearSVC,SVC
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import TomekLinks,ClusterCentroids
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from tqdm import tqdm
def get_data(data_file):
    transactions=pd.read_csv(data_file)
    x_sampled=transactions
    y_sampled=transactions["Class"]
    splitter=StratifiedShuffleSplit(test_size=0.15,n_splits=5)
    spl=splitter.split(x_sampled, y_sampled)
    for train_index, test_index in spl:
        x_train,x_test=x_sampled.loc[train_index,:],x_sampled.loc[test_index,:]
        
    
    #print(x_sampled.shape,x_train.shape,x_test.shape,y_train[y_train==1].count()/y_train.count(),y_test[y_test==1].count()/y_test.count())
    x_train=x_train.reset_index()
    x_test=x_test.reset_index()
   
    return x_train,x_test
   

def visualize(train_data):
    targets=train_data["Class"]
    train_data.drop("Class",axis=1,inplace=True)
    pca=PCA(n_components=2)
    train_data_2d=pca.fit_transform(train_data)
    plt.scatter(train_data_2d[:,0],train_data_2d[:,1],c=targets)
    
    plt.show()
    
 
def pre_process(transactions,test):
   
    sampler=SMOTE()
    targets=transactions["Class"]
    y_test=test["Class"]
    transactions.drop("Class",axis=1,inplace=True)
    test.drop("Class",axis=1,inplace=True)
    
    
    
    splitter=StratifiedShuffleSplit(test_size=0.15,n_splits=5,random_state=42)
    spl=splitter.split(transactions,targets)
    for train_index, val_index in spl:
    
        y_train,y_val=targets[train_index],targets[val_index]
        x_train,x_val=transactions.loc[train_index,:],transactions.loc[val_index,:]
        
        
    print(x_train.shape,x_val.shape,y_train[y_train==0].count()/y_train[y_train==1].count(),y_val[y_val==0].count()/y_val[y_val==1].count())
    x_sampled_train,y_sampled_train=sampler.fit_resample(x_train,y_train)
    transformer=StandardScaler()
    x_sampled_train=transformer.fit_transform(x_sampled_train)
    x_val=transformer.transform(x_val)
    x_test=transformer.transform(test)
    return(x_sampled_train,y_sampled_train),(x_val,y_val),(x_test,y_test)

    

def train(train,validation):
    model=RandomForestClassifier(n_estimators=516,random_state=42)
    
    #model=XGBClassifier(use_label_encoder=False,learning_rate=0.1,n_estimators=516,max_depth=4,min_child_weight=4,seed=42,scale_pos_weight=1)
    train_x,train_y=train[0],train[1]
    val_x,val_y=validation[0],validation[1]
    #parameter tuning to get the optimum no of estimators
    def optimal_num_estimators(model,predictors,targets,cv_folds=5,early_stopping_rounds=50):
        xgb_params=model.get_xgb_params()
        xgtrain=xgb.DMatrix(predictors,label=targets)
        cv_result=xgb.cv(xgb_params,xgtrain,num_boost_round=1000,nfold=cv_folds,metrics="auc",early_stopping_rounds=early_stopping_rounds)
        model.set_params(n_estimators=cv_result.shape[0])
        print(cv_result.shape[0])#no_of_estimators=516
        return model
    #model=optimal_num_estimators(baseline_model,train_x,train_y) 
    
   # param_grid={
        #"max_depth":[3,4,5],
        #"min_child_weight":[2,3,5],
        #"learning_rate":[0.05,0.1,0.01,0.2]}
        #"reg_alpha":[0.01,0.005,0.1]}
   
    #gridSearch=GridSearchCV(model,param_grid,verbose=20,n_jobs=-1,return_train_score=True)
    #gridSearch.fit(train_x,train_y)
    #model=gridSearch.best_estimator_
    print(model)
    
    model.fit(train_x,train_y)
    val_y_pred=model.predict(val_x)
    val_y_pred_prob=model.predict_proba(val_x)[:,1]
    conf_mat_val=confusion_matrix(val_y,val_y_pred)
    precis_val=precision_score(val_y,val_y_pred)
    recall_val=recall_score(val_y,val_y_pred)
    roc_auc=roc_auc_score(val_y,val_y_pred_prob)
    print(conf_mat_val,precis_val,recall_val,roc_auc)
    
    
    return model
    pass

def predict(model,test):
    test_x=test[0]
    test_y=test[1]
    test_y_pred=model.predict(test_x)
    conf_mat_test=confusion_matrix(test_y,test_y_pred)
    precis_test=precision_score(test_y,test_y_pred)
    recall_test=recall_score(test_y,test_y_pred)
    print(conf_mat_test,precis_test,recall_test)
    pass

def main(data_file):
    training_data,testing_data=get_data(data_file)
    training,val,test=pre_process(training_data,testing_data)
    model=train(training,val)
    #predict(model,test)
    
   # visualize(transactions)
    pass

if __name__=="__main__":
    creditcard_file=r"data sources\creditcard_\creditcard.csv"
    main(creditcard_file)

    
    
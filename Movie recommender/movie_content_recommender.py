# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 14:07:27 2020

@author: Administrator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#from ast import literal_eval
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel,cosine_distances
def get_data(file,file2):
    data=pd.read_csv(file,usecols=['movie_id','title','cast','crew'],low_memory=False)
    data2=pd.read_csv(file2)
    return data,data2
def preprocess_movie(data):
   # print(data.columns)
    data=data[["genres","production_countries","keywords","production_companies","title","id"]]
    #print(data.shape)
    json_cols=[]
    for col in data.columns:
        if data[col].dtype=="object":
            if data[col][0].startswith("["):
                json_cols.append(col)
   # print(json_cols)
    def change_type(x):
        return json.loads(x)
    new_data=data.copy()
    for cols in json_cols:
        new_data[cols]=data[cols].apply(change_type)
   # print( new_data.loc[np.random.randint(4000),"keywords"])
    def create_word_bag(y,thresh,lens):
        if isinstance(y,list) and len(y)>0:
            if len(y)>=thresh:
                list_names=[i["name"] for i in y[:lens]]
            else:
                list_names=[i["name"] for i in y]
           
            
            return "|" . join (list_names)
        else:
            return np.nan
    def join_words(x):
        if " " in str(x):
            return str(x).replace(" ","")
        else:
            return x
        
    for cols in json_cols:
        if cols=="genres":
            new_data[cols]=new_data[cols].apply(create_word_bag,args=[5,4])
        elif cols=="keywords":
            new_data[cols]=new_data[cols].apply(create_word_bag,args=[3,2])
        else:
            new_data[cols]=new_data[cols].apply(create_word_bag,args=[3,2])
        new_data[cols]=new_data[cols].apply(join_words)
    new_data.dropna(inplace=True)
    
    new_data=new_data.reset_index().drop("index",axis=1)
    new_data["features"]=new_data["genres"]+" "+ new_data["production_countries"]+" "+new_data["keywords"]+" "+new_data["production_companies"]
    #print(new_data.loc[np.random.randint(0,4000,20),"title"])
    tfid=TfidfVectorizer(stop_words="english")
    word_matrix=tfid.fit_transform(new_data["features"])
    return word_matrix,new_data
    
    
    
def preprocess_cred(data):
    data.dropna(inplace=True)
    def change_type(x):
        return json.loads(x) 
    data=data.copy()[ data['crew'].str.endswith("]")]
    data["new_crew"]=data["crew"].apply(change_type)
    data['new_cast']=data['cast'].apply(change_type)
    data.drop(['crew','cast'],axis=1,inplace=True)
    def create_word_bag_2(x,crew=False):
        if isinstance(x, list) and len(x)>0:
            if crew==False:
                if len(x)>3:
                    list_names=[i["name"] for i in x[:3]]
                else:
                    list_names=[i["name"] for i in x]
            else:
                list_names=[i["name"] for i in x if i["job"]=="Director"]
            return "|".join(list_names)
        else:
            return np.nan
    def join_words_2(x):
        if " " in str(x):
            return str(x).replace(" ","")
        else:
            return x
    
    data["new_cast"]=data["new_cast"].apply(create_word_bag_2)
    data["new_cast"]=data["new_cast"].apply(join_words_2)
    data["new_crew"]=data["new_crew"].apply(create_word_bag_2,args=[True])
    data["new_crew"]=data["new_crew"].apply(join_words_2)
    data["movie_id"]=data["movie_id"].astype(int)    
    data.dropna(inplace=True)
    data=data.reset_index().drop("index",axis=1)
    data["features_2"]=data["new_cast"]+" "+data["new_crew"]
    #print(data.features.head(),data.title.head())
   
    coun=TfidfVectorizer(stop_words="english")
    word_matrix=coun.fit_transform(data["features_2"])
    
    return word_matrix,data
    #return data
def engineer_features(mov_data,crew_data):
    
    comp_data=pd.merge(mov_data,crew_data,left_on="id",right_on="movie_id",how="inner")
    comp_data.drop("title_y",axis=1,inplace=True)
    comp_data=comp_data.rename({"title_x":"title"},axis=1)
    
    comp_data["total_features"]=comp_data["features"]+" "+comp_data["features_2"]
    cout=CountVectorizer(stop_words="english")
    word_matrix=cout.fit_transform(comp_data["total_features"])
    return word_matrix,comp_data
def train_model(word_matrix):
    nearest_neibs=cosine_distances(word_matrix)
    x=np.argsort(nearest_neibs)
    return x
def get_recommendations(movie,similarity,movie_table):
    movie=movie.lower().strip()
    movie_table["title"]=movie_table["title"].str.lower()
    indx=movie_table[movie_table["title"]==movie].index
    try:
        movie_recomm=similarity[indx,1:21]
        movie_recomm=movie_recomm.reshape(movie_recomm.shape[1])
        movie_recomm=movie_table.loc[movie_recomm,"title"]
        print(movie_recomm[movie_recomm!=movie])
        recommended_movies=movie_recomm[movie_recomm!=movie]
        return recommended_movies
    except Exception:
        print(f"This movie,'{movie}',cannot be found")
    
    
def main(movi,cred,movie_name):
    cred_df,movi_df=get_data(cred,movi)
    movie_mtx_data=preprocess_movie(movi_df)
    crew_cast_mtx_data=preprocess_cred(cred_df)
    complete_mtx_data=engineer_features(movie_mtx_data[1],crew_cast_mtx_data[1])
    
    movie_details=[crew_cast_mtx_data,movie_mtx_data,complete_mtx_data]
        
    similarity=train_model(movie_details[recomm_type-1][0])
    get_recommendations(movie_name, similarity,movie_details[recomm_type-1][1])
def execute(first=True):
    def get_mov_name():
        movie_name=input("Hi,what movie do you like?\n ")
        return movie_name
    def get_type_recomm(movie_name,first):
        
        if first:
            recomm_type=input(f"Interesting choice i must say,why do you like this movie,'{movie_name}'?Could it be \n 1. The cast and their style of acting?\n \
2. The genre it belongs to and theme/plot of the movie? \n 3. Both of the previous options? \n \
   Please reply 1,2,or 3 corresponding to your choice\n ")
        else:
            recomm_type=input(f"Your choice must be either of the values '1, 2, 3', Please reply 1,2,or 3 corresponding to your choice\n  ")
        return recomm_type
    def get_recom_bool(movie_name):
        recomm_bool=input(f"Do you want me to recommend movies similar to '{movie_name}' based on your preference? Please reply y/n for yes/no \n")
        return recomm_bool
    global recomm_bool
    global recomm_type
    if first:
        try:
            global movie_name
            movie_name=get_mov_name()
            
        except Exception:
            execute(False)
        try:    
            recomm_type=int(get_type_recomm(movie_name,first))
            if recomm_type not in[1,2,3]:
                 execute(False)
            else:
                recomm_bool=get_recom_bool(movie_name)
                
        except ValueError:
            execute(False)
      
    else:
        try:    
            recomm_type=int(get_type_recomm(movie_name,first))
            if recomm_type not in[1,2,3]:
                 execute(False)
            else:
                recomm_bool=get_recom_bool(movie_name)
               
        except ValueError:
            execute(False)
    return 
if __name__=="__main__":
    movie_file= r"data sources\tmdb_5000_credits\tmdb_5000_movies.csv"
    credits_file=r"data sources\tmdb_5000_credits\tmdb_5000_credits.csv"
    
    execute()
    #movie_name=execute1()
    #recomm_type=execute2()
    #execute3()
    main(movie_file,credits_file,movie_name)
    
'''  Final Fantasy: The Spirits Within
1616          Snow White and the Huntsman
3732                            Amores perros          
242           The Hobbit: The Desolation of Smaug
3288                                The Ten
1013                                Solaris
2601                 The Godfather: Part II
2314        I Know What You Did Last Summer
1871                        Michael Collins
1149                          Julie & Julia
3159                           March or Die
161                                Watchmen
2149                          Sweet Charity
277                          Public Enemies
363                         The Interpreter
3963                        The Poker House
3132                            The Descent
3393                            Born Of War
1864                              Draft Day
3484                              Red State
3857                          The Dog Lover
1081                  Johnny English Reborn
647                          Blade: Trinity    
2666                              Machete
Standard Operating Procedure
415           Hellboy II: The Golden Army
3816                      Grace Unplugged
1905        Star Trek IV: The Voyage Home
1071                          The Phantom
1507                            Toy Story
3032              Repo! The Genetic Opera
2478                  Eye of the Beholder
1053            Resident Evil: Extinction
2709                          Paper Towns
142                 Mr. Peabody & Sherman
2431                When a Stranger Calls
3245            The Business of Stranger               
1776       Scooby-Doo 2: Monsters Unleashed '''  
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 03:56:39 2021

@author: Administrator
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from collections import defaultdict
from uuid import uuid4
import re
import random
import pickle
from ast import literal_eval
import pandas as pd


def scrape(container):
    selectors=[".lister-item-header a",".text-muted.unbold","strong","span.runtime","span.genre",".ratings-bar +.text-muted"]
    selector_details=["Title","Release Year","Imdb_rating","Duration","Genre","Summary"]
   
    def find_cast_director():
        cast_dir=WebDriverWait(driver, 7).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,container)))
        cast_dir=driver.find_element_by_css_selector(container).find_elements_by_tag_name("p")[-2:]
        cast_dir=[names_.text for names_ in cast_dir]
        
        cast_dir="|".join(cast_dir).split("|")
        cast_list=[]
        for info in cast_dir:
            if ":" in info:
                info=info.split(":")
                info[0]=str(info[0]).strip().title()
                
                if ", " in info[1]:
                    info[1]=info[1].split(",")
                
                if info[0]=="Director" or info[0]=="Directors":
                    info[0]="Director(s)"
                elif info[0]=="Star" or info[0]=="Stars":
                    info[0]="Star(s)"
                cast_list.append(info[0])
                cast_dir_dict[info[0]].append(info[1])
        for k in cast_dir_dict.keys():
            if k not in cast_list:
                cast_dir_dict[k].append(None)
        return 
    def find_movie_detail(styling,count):
            movie_detail=WebDriverWait(driver, 7).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,styling)))
            movie_detail=driver.find_elements_by_css_selector(styling)
            movie_detail=[data.text for data in movie_detail]
            movie_detail_dict[selector_details[count]].append(movie_detail)
            return
    def find_more_details():
        id_="titleDetails"
        more_details=WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.ID,id_)))
        more_details=driver.find_element_by_id(id_).find_elements_by_class_name("txt-block")
        det=[detail.text for detail in more_details]
        val_list=[]
        for value in det:
            if ":" in value:
                value=value.split(":")
                value[0]=str(value[0]).strip().title()
                
                if value[0] in ["Country","Language","Production Co"]:
                    val_list.append(value[0])
                    if "," in value[1]:
                        value[1]=value[1].split(",")
                        for i in range(len(value[1])):
                            if isinstance(value[1][i], str) and "see more" in value[1][i].strip().lower():
                                see_ind=value[1][i].lower().index("see more")
                                value[1][i]=value[1][i][:see_ind]
                    elif "|" in value[1]:
                        value[1]=value[1].split("|")
                        for i in range(len(value[1])):
                            if isinstance(value[1][i], str) and "see more" in value[1][i].strip().lower():
                                see_ind=value[1][i].lower().index("see more")
                                value[1][i]=value[1][i][:see_ind]
                    else:
                        if isinstance(value[1], str) and "see more" in value[1].strip().lower():
                                see_ind=value[1].lower().index("see more")
                                value[1]=value[1][:see_ind]
                    detail_dict[value[0]].append(value[1])
        for k in detail_dict.keys():
            if k not in val_list:
                detail_dict[k].append(None)
        return 
    
    try:
        find_cast_director()
    except  Exception or TimeoutException or NoSuchElementException or StaleElementReferenceException:
        try :
            find_cast_director()
        except Exception or NoSuchElementException:
            for k in cast_dir_dict.keys():
                cast_dir_dict[k].append(None)
    #print(cast_dir_dict)
    
    
    
    for i in range(len(selectors)):
        styling=container+selectors[i]
        try:
            find_movie_detail(styling,i)
            
        except Exception or TimeoutException or NoSuchElementException or StaleElementReferenceException:
            try:
                find_movie_detail(styling,i)
            except Exception or NoSuchElementException :
                movie_detail_dict[selector_details[i]].append(None)
    movie_detail_dict["Id"].append(str(uuid4())+movie_detail_dict["Title"][-1][0])               
    #print(movie_detail_dict)
    clickable_header=True
    try:
        header=driver.find_element_by_css_selector(container+selectors[0])
        header.click()
    except Exception or TimeoutException or NoSuchElementException or StaleElementReferenceException :
        try:
            driver.refresh()
            header=driver.find_element_by_css_selector(container+selectors[0])
            header.click()
        except Exception or NoSuchElementException:
            clickable_header=False
    if clickable_header:        
        try:
            find_more_details()
            driver.back()
           
        except Exception or TimeoutException or NoSuchElementException or StaleElementReferenceException :
            try:
                driver.refresh()
                find_more_details()
                driver.back()
            except  Exception or NoSuchElementException :
                for k in detail_dict.keys():
                    detail_dict[k].append(None)
                
                driver.back()
    else:
        for k in detail_dict.keys():
            detail_dict[k].append(None)
    #print(detail_dict)
    return 
def scrape_containers():
    def get_containers():
        containers=".mode-advanced"
        container_elements=WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,containers)))
        container_elements=driver.find_elements_by_css_selector(containers)
        return container_elements
   
    try:
        container_elements=get_containers()
    except TimeoutException or StaleElementReferenceException :
        try:
            driver.refresh()
            container_elements=get_containers()
        except:
            return
        else:
            sample=[i for i in range(len(container_elements))]
            sample=random.sample(sample, 35)
            for i in sample:
                container=f".mode-advanced:nth-child({i+1}) "
                scrape(container)
                time.sleep(1)
    except Exception or NoSuchElementException:
        return
    else:    
        sample=[i for i in range(len(container_elements))]
        sample=random.sample(sample, 35)
        for i in sample:
            container=f".mode-advanced:nth-child({i+1}) "
            scrape(container)
            time.sleep(2)
    
    return
def navigate():
    def find_next_link():
        next_link=".next-page"
        next_link_elelments=WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,next_link)))
        next_link_elelments=driver.find_elements_by_css_selector(next_link)
        return next_link_elelments
    try:
        next_link_elements=find_next_link()
        next_link_elements[0].click()
        
    except TimeoutException or StaleElementReferenceException :
        driver.refresh()
        next_link_elements=find_next_link()
        next_link_elements[0].click()
    except Exception or NoSuchElementException:
        try:
            current_page_url=str(driver.current_url)
            c=re.findall("&start=\d+&",current_page_url)
            page_number=re.findall("\d+",c[0])[0]
            d=50+int(page_number)
            next_page_url=re.sub("&start=\d+&", f"&start={d}&",current_page_url)
            print(next_page_url)
            driver.get(next_page_url)
        except:
            print("Stopped navigating at ",driver.current_url)
            
            return False
                
    return True
    
def save_file(pickle_file,csv_file):
    with open(pickle_file,"rb") as f:
        mpv=pickle.load(f)
    mpvd=pd.DataFrame(mpv)
    mpvd["Title"]=[x[0] if isinstance(x,list) else x for x in mpvd["Title"] ]
    mpvd["Release Year"]=[x[0] if isinstance(x,list) else x for x in mpvd["Release Year"]]
    mpvd["part"]=mpvd["Release Year"].str.extract ("(\([A-Za-z]+\))")
    mpvd["Release Year"]=mpvd["Release Year"].str.extract("([0-9]+)")
    mpvd["part"].fillna('',inplace=True)
    mpvd["Title"]+=" "+mpvd["part"]
    mpvd.drop(axis=1,columns=["part"],inplace=True)
    duplicates=mpvd.copy()[~mpvd["Title"].duplicated()]
    duplicates.reset_index(inplace=True)
    duplicates.drop(axis=1,columns=["index"],inplace=True)
    duplicates.to_csv(csv_file)
    return
def save_pickle_file(filename2):
    with open(filename2,"wb") as f:
        pickle.dump(complete_movie_detail_dict ,f)
    return
def empty_sub_dictionaries():
    for k in cast_dir_dict.keys():
        cast_dir_dict[k]=[]
    for k in movie_detail_dict.keys():
        movie_detail_dict[k]=[]
    for k in detail_dict.keys():
        detail_dict[k]=[]
    return
def update_dictionary():
    for k in complete_movie_detail_dict.keys():
        if isinstance(complete_movie_detail_dict[k] ,str):
            complete_movie_detail_dict[k]=literal_eval(complete_movie_detail_dict[k])
        else:
            pass
        if k in cast_dir_dict.keys():
            complete_movie_detail_dict[k]+=cast_dir_dict[k]
        elif k in detail_dict.keys():
            complete_movie_detail_dict[k]+=detail_dict[k]
        else:
            complete_movie_detail_dict[k]+=movie_detail_dict[k]
    empty_sub_dictionaries()
    return


def main():
    global cast_dir_dict
    global movie_detail_dict
    global detail_dict
    global complete_movie_detail_dict
    cast_dir_dict={"Director(s)":[],"Star(s)":[],"Votes":[],"Gross":[]}
    movie_detail_dict=defaultdict(list)
    detail_dict={"Country":[],"Language":[],"Production Co":[]}
    with open (FILEPATH_PICKLE,"rb") as f2:
        complete_movie_detail_dict=pickle.load(f2)
    
    try:
        print(len(complete_movie_detail_dict["Id"]))
        scrape_containers()
        update_dictionary()
        save_pickle_file(FILEPATH_PICKLE)
        print(len(complete_movie_detail_dict["Id"]))
        while len(complete_movie_detail_dict["Id"])<=3000:
            nav_check=navigate()
            print(driver.current_url)
            if nav_check:
                scrape_containers()
                update_dictionary()
                save_pickle_file(FILEPATH_PICKLE)
                
            else:
                print(driver.current_url)
                break
            print(len(complete_movie_detail_dict["Id"]))  
        else:
            print("Finished")
            save_file(FILEPATH_PICKLE,FILEPATH_CSV)
    except Exception as e:
        print (e)
        save_pickle_file(FILEPATH_PICKLE)
        
    return
if __name__=="__main__":
    PATH=r"C:\Program Files (x86)\chromedriver.exe"
    driver=webdriver.Chrome(PATH)
    URL="https://www.imdb.com/search/title/?title_type=feature&year=2017-01-01,2017-12-31&start=1&ref_=adv_nxt"
    driver.get(URL)
    FILEPATH_CSV=r"C:\Users\MARVIN\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb.csv"
    FILEPATH_PICKLE=r"C:\Users\MARVIN\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb_dictionary"
    main()
    
        

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


def scrape(container:str)->None:
    """
    Args : container - css_selector of a single movie container_element
    
    Takes selector and collects details ( "Title","Release Year","Imdb_rating","Duration","Genre","Summary","Language","Cast",
    "Director","Production_companies)of the movie
    """
    #css selectors and their corresponding fields
    selectors=[".lister-item-header a",".text-muted.unbold","strong","span.runtime","span.genre",".ratings-bar +.text-muted"]
    selector_details=["Title","Release Year","Imdb_rating","Duration","Genre","Summary"]
   
    def find_cast_director():
        #extracting the movie cast, director and votes
        cast_dir=WebDriverWait(driver, 7).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,container)))
        cast_dir=driver.find_element_by_css_selector(container).find_elements_by_tag_name("p")[-2:]
        cast_dir=[names_.text for names_ in cast_dir]
        #Separating the cast, director and votes into 3 separate list values
        cast_dir="|".join(cast_dir).split("|")
        cast_list=[]
        #Splitting the field:value string into key:value dict item e.g"cast: name"->"cast":"name"
        for info in cast_dir:
            if ":" in info:
                info=info.split(":")
                info[0]=str(info[0]).strip().title()
                
                if ", " in info[1]:
                    info[1]=info[1].split(",")
                #singular and plural key names into a single key name
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
            """
            Obtain general details about the movie; Title, Genre, Release Year, rating, Duration, Genre, Summary
            """
            movie_detail=WebDriverWait(driver, 7).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,styling)))
            movie_detail=driver.find_elements_by_css_selector(styling)
            movie_detail=[data.text for data in movie_detail]
            movie_detail_dict[selector_details[count]].append(movie_detail)
            return
    def find_more_details():
        """
        Obtain more details about the movie, such as Language, Production companies, Countries of origin
        """
        detail_selectors=["releasedate","origin","languages","companies"]
        val_list=[]
        for sel in detail_selectors:

            lang_details= driver.find_element_by_css_selector(f"li[data-testid='title-details-{sel}'")
            field=lang_details.find_element_by_css_selector(".ipc-metadata-list-item__label").text
            data_=lang_details.find_element_by_css_selector("div.ipc-metadata-list-item__content-container").find_elements_by_css_selector("li[role='presentation']")
            if "language" in field.lower():
                field="Language(s)"
            elif "countr" in field.lower():
                field="Country_of_origin"
            elif "production" in field.lower():
                field="Production_companies"
            elif "release" in field.lower():
                field="Release_date"
            field_values=[det.text for det in data_]
            detail_dict[field].append(field_values)
            val_list.append(field)
        poster_image=driver.find_element_by_css_selector(".ipc-lockup-overlay__screen")
        poster_image.click()
        close_det= driver.find_element_by_css_selector(".media-sheet__close")
        close_det.click()
        image_selector="div img"
        WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,image_selector)))
        image=driver.find_element_by_css_selector(image_selector)
        time.sleep(2)
        img_src=image.get_attribute("src")
        driver.back()
        if img_src:
            image_key="Poster_image"
            detail_dict[image_key].append(img_src)
            val_list.append(image_key)
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
    """
    Collects details of 80% of the movies on the current navigated page
    """
    def get_containers():
        """
        Returns a list of all movies (with their details) on the current page
        """
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
            #randomly selecting 80% of the list of movies on the current navigated page
            sample=[i for i,_ in enumerate(container_elements)]
            sample=random.sample(sample, 2)
            for i in sample:
                container_css=f".mode-advanced:nth-child({i+1}) "
                scrape(container_css)
                time.sleep(1)
    except Exception or NoSuchElementException:
        return
    else:    
        sample=[i for i,_ in enumerate(container_elements)]
        sample=random.sample(sample, 2)
        for i in sample:
            container_css=f".mode-advanced:nth-child({i+1}) "
            scrape(container_css)
            time.sleep(2)
    print(detail_dict, "\n", movie_detail_dict, "\n", cast_dir_dict)
    return
def navigate():
    def find_next_link():
        next_link=".next-page"
        next_link_elelments=WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,next_link)))
        next_link_elelments=driver.find_elements_by_css_selector(next_link)
        return next_link_elelments
    try:
        #Navigate to the next page of current page
        next_link_elements=find_next_link()
        next_link_elements[0].click()
        
    except TimeoutException or StaleElementReferenceException :
        driver.refresh()
        next_link_elements=find_next_link()
        next_link_elements[0].click()
    except Exception or NoSuchElementException:
        try:
            #Directly modifying the url to navigate to the next page in event of an error
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
    #loading the dict of previously scraped movie details and appending new movies and their details
    with open(pickle_file,"rb") as f:
        mpv=pickle.load(f)
    mpvd=pd.DataFrame(mpv)
    #ensure all movie titles and release year are strings
    mpvd["Title"]=[x[0] if isinstance(x,list) else x for x in mpvd["Title"] ]
    mpvd["Release Year"]=[x[0] if isinstance(x,list) else x for x in mpvd["Release Year"]]
    #Further cleaning to separate the movie part from the release year
    mpvd["part"]=mpvd["Release Year"].str.extract ("(\([A-Za-z]+\))")
    mpvd["Release Year"]=mpvd["Release Year"].str.extract("([0-9]+)")
    mpvd["part"].fillna('',inplace=True)
    mpvd["Title"]+=" "+mpvd["part"]
    mpvd.drop(axis=1,columns=["part"],inplace=True)
    #Removing duplicates
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
    """
    Emptying all the sub-dictionaries after every page navigation to prevent duplication of data
    """
    for k in cast_dir_dict.keys():
        cast_dir_dict[k]=[]
    for k in movie_detail_dict.keys():
        movie_detail_dict[k]=[]
    for k in detail_dict.keys():
        detail_dict[k]=[]
    return
def update_dictionary():
    """
    Update the super-dictionary with the sub-dictionaries
    """
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
    #Sub-dictionaries
    global cast_dir_dict#Holds data about the Cast and Diector(s) of a movie
    global movie_detail_dict#Holds data about the Title, genre, release date, rating e.t.cof a movie
    global detail_dict#Holds data about more details (language, country, production companies) of the movie
    global complete_movie_detail_dict#Super-dictionary
    cast_dir_dict={"Director(s)":[],"Star(s)":[],"Votes":[],"Gross":[]}
    movie_detail_dict=defaultdict(list)
    detail_dict={"Language(s)":[],"Country_of_origin":[],"Production_companies":[],"Poster_image":[],"Release_date":[]}
    try:
        with open (FILEPATH_PICKLE,"rb") as f2:
            complete_movie_detail_dict=pickle.load(f2)
    except FileNotFoundError:
        complete_movie_detail_dict=defaultdict(list)
    try:
        scrape_containers()
        import sys
        sys.exit()
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
    FILEPATH_CSV=r"C:\Users\DELL\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb.csv"#File_path of movie_data files
    FILEPATH_PICKLE=r"C:\Users\DELL\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb_dictionary"##File_path of pickle file
    main()
    
        

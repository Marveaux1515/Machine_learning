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
    
    Takes selector and collects details ( "Title","Imdb_rating","Duration","Genre","Summary","Language","Cast",
    "Director","Production_companies)of the movie
    """
    #css selectors and their corresponding fields
    selectors=[".lister-item-header a","strong","span.runtime","span.genre",".ratings-bar +.text-muted",".certificate"]
    selector_details=["Title","Imdb_rating","Duration","Genre","Summary","MPA_rating"]
   
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
            try:
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
            except Exception as e:
                print("Error \t", e)
                pass
        try:
            poster_image=driver.find_element_by_css_selector(".ipc-lockup-overlay__screen")
            poster_image.click()
            close_det= driver.find_element_by_css_selector(".media-sheet__close")
            close_det.click()
            image_selector="div img[class='MediaViewerImagestyles__PortraitImage-sc-1qk433p-0 bnaOri']"
            WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,image_selector)))
            image=driver.find_element_by_css_selector(image_selector)
            time.sleep(1)
            img_src=image.get_attribute("src")
            if img_src:
                image_key="Poster_image"
                detail_dict[image_key].append(img_src)
                val_list.append(image_key)
        except Exception as e:
            print("Error \t", e)
            pass
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
            
        except:
            try:
                find_movie_detail(styling,i)
            except Exception as e :
                print("Error \t", e)
                movie_detail_dict[selector_details[i]].append(None)
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
        find_more_details()
        driver.get(curr_url)
    else:
        for k in detail_dict.keys():
            detail_dict[k].append(None)
    return 
def scrape_containers(start_point:int):
    """
    Collects details of the movies on the current navigated page
    Args: start_point - movie-number to start scraping from
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
    global curr_url
    curr_url=driver.current_url
    save_url(curr_url)
    try:
        container_elements=get_containers()
    except TimeoutException or StaleElementReferenceException :
        try:
            driver.refresh()
            container_elements=get_containers()
        except:
            return
        else:
            if not start_point:
                sample=[i for i,_ in enumerate(container_elements)]
            else:
                sample=[i for i in range(start_point,len(container_elements))]
            for i in sample:
                if i%10==0 and i!=0:
                    update_dictionary()
                    save_pickle_file(FILEPATH_PICKLE)
                    save_file(FILEPATH_PICKLE,FILEPATH_CSV)
                container_css=f".mode-advanced:nth-child({i+1}) "
                scrape(container_css)
                time.sleep(1)
    except Exception or NoSuchElementException:
        return
    else:    
        if not start_point:
            sample=[i for i,_ in enumerate(container_elements)]
        else:
            sample=[i for i in range(start_point,len(container_elements))]
        for i in sample:
            if i%10==0 and i!=0:
                update_dictionary()
                save_pickle_file(FILEPATH_PICKLE)
                save_file(FILEPATH_PICKLE,FILEPATH_CSV)
            container_css=f".mode-advanced:nth-child({i+1}) "
            scrape(container_css)
            time.sleep(1)
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
    """
    Minor cleaning of the scraped movie details and saving to csv_file
    """
    #loading the dict of previously scraped movie details and appending new movies and their details
    with open(pickle_file,"rb") as f:
        mpv=pickle.load(f)
    mpvd=pd.DataFrame(mpv)
    #ensure all movie titles and release year are strings
    mpvd["Title"]=[x[0] if isinstance(x,list) else x for x in mpvd["Title"]]
    #Further cleaning to extract the movie release date
    mpvd["Release_date"]=[x[0] if isinstance(x,list) else x for x in mpvd["Release_date"]]
    mpvd["Release_date"]=mpvd["Release_date"].str.replace("\(.+\)","")
    
    mpvd["Release_date"]=pd.to_datetime(mpvd["Release_date"]) 
    #Removing duplicates
    non_duplicates=mpvd.copy()[~mpvd[["Title","Release_date"]].duplicated()]
    non_duplicates.reset_index(inplace=True)
    non_duplicates.drop(axis=1,columns=["index"],inplace=True)
    print(non_duplicates[["Title","Release_date"]])
    non_duplicates.to_csv(csv_file)
    return
def save_pickle_file(filename2):
    """
    Saving the binary file for reference purposes
    """
    with open(filename2,"wb") as f:
        pickle.dump(complete_movie_detail_dict ,f)
    return
def save_url(c_url):
    """
    save the url of the current page in event of a network interruption
    Args: c_url - url of the current navigated pseudo-Homepage
    """
    with open (FILEPATH_URL,"a") as url_f:
        url_f.write(c_url+"\n")
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
def check_dictionary(k):
    """
    Checks if the super dictionary has items and converts the dict_values to their literal data type
    """
    if len(complete_movie_detail_dict)>0:
        if isinstance(complete_movie_detail_dict[k] ,str):
             complete_movie_detail_dict[k]=literal_eval(complete_movie_detail_dict[k])
    return
def update_dictionary():
    """
    Update the super-dictionary with the sub-dictionaries
    """
    
    for k in cast_dir_dict.keys():
        check_dictionary(k)
        complete_movie_detail_dict[k]+=cast_dir_dict[k]
    for k in detail_dict.keys():
        check_dictionary(k)
        complete_movie_detail_dict[k]+=detail_dict[k]
    for k in movie_detail_dict.keys():
        check_dictionary(k)
        complete_movie_detail_dict[k]+=movie_detail_dict[k]
    empty_sub_dictionaries()
    return

def load_checkpoints():
    """
    Returns the Imdb movies url from last scraping session (if any) and also the last saved movie number 
    when the last scraping session was interrupted/stopped  
    """
    with open (FILEPATH_PICKLE,"rb") as f2:
         movies_dictionary=pickle.load(f2)
    num_movies=len(movies_dictionary["Title"])
    if num_movies%50 !=0 and num_movies!=0:
        start_point=num_movies%50
    else:
        start_point=None
    try:
        with open(FILEPATH_URL, "r") as urlf_buff:
            URL=urlf_buff.readlines()[-1]
    except FileNotFoundError:
        if start_point:
            url_start_point=num_movies-start_point+1
        else:
            url_start_point=num_movies+1
        URL=f"https://www.imdb.com/search/title/?title_type=feature&year=2021-01-01,2021-12-31&start={url_start_point}&ref_=adv_nxt"#Base url of Imdb featured movies
    return URL,start_point
def main(start_point:int):
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
        scrape_containers(start_point)
        update_dictionary()
        save_pickle_file(FILEPATH_PICKLE)
        save_file(FILEPATH_PICKLE,FILEPATH_CSV)
        while len(complete_movie_detail_dict["Title"])<=3000:
            nav_check=navigate()
            print(driver.current_url)
            if nav_check:
                scrape_containers(None)
                update_dictionary()
                save_pickle_file(FILEPATH_PICKLE)
                save_file(FILEPATH_PICKLE,FILEPATH_CSV)
                
            else:
                save_url(curr_url)
                break
        else:
            print("Finished")
            save_file(FILEPATH_PICKLE,FILEPATH_CSV)
    except Exception as e:
        print (e)
        update_dictionary()
        save_pickle_file(FILEPATH_PICKLE)
        save_url(curr_url)
    return
if __name__=="__main__":
    PATH=r"C:\Program Files (x86)\chromedriver.exe"
    FILEPATH_CSV=r"C:\Users\DELL\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb.csv"#File_path of movie_data files
    FILEPATH_PICKLE=r"C:\Users\DELL\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb_dictionary"#File_path of pickle file
    FILEPATH_URL=r"C:\Users\DELL\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\Imdb_url.txt" #Text file containing the base url when an unhandled exception (e.g network disruption) is thrown
    URL,start_point=load_checkpoints()
    driver=webdriver.Chrome(PATH)
    driver.get(URL)
    main(start_point)
    # with open (FILEPATH_PICKLE,"rb") as f2:
    #     complete_movie_detail_dict=pickle.load(f2)
    # for k in complete_movie_detail_dict.keys():
    #     print(k,"\t",len(complete_movie_detail_dict[k]))
    # print(complete_movie_detail_dict["Title"][950:960])
    # with open (FILEPATH_PICKLE,"wb") as f2:
    #     pickle.dump(complete_movie_detail_dict ,f2)
    
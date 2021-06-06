# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 05:15:51 2021

@author: Administrator
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
def main():
   
    
    
    container=".mode-advanced:nth-child(1) .lister-item-header a"
    
    header=driver.find_element_by_css_selector(container)
    header.click()
    
    id_="titleStoryLine"
    more_details=WebDriverWait(driver, 8).until(
              EC.presence_of_element_located((By.ID,id_)))
    more_details=driver.find_element_by_id(id_).find_elements_by_class_name("itemprop")
    det=[detail.text for detail in more_details]
    image=driver.find_element_by_css_selector(".poster img")
    src=image.get_attribute("src")
    driver.get(src)
    
    
    
    image_path=r"C:\Users\MARVIN\Desktop\D_SCIENCE\practicals\python files\data sources\Imdb_movie_details\movie.png"
    driver.save_screenshot(image_path)
    return
if __name__=="__main__":
    PATH="C:\Program Files (x86)\chromedriver.exe"
    driver=webdriver.Chrome(PATH)
    URL="https://www.imdb.com/search/title/?title_type=feature&year=2017-01-01,2017-12-31&start=1&ref_=adv_nxt"
    driver.get(URL)
    main()
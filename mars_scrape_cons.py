# Importing all dependencies

import time
import pandas as pd
import numpy as np
import requests as req
import os

from bs4 import BeautifulSoup as bs
from splinter import browser
from selenium import webdriver
from urllib.parse import urlsplit

def init_browser():
    executable_path = {'executable_path' : 'chromedriver'}
    browser = browser('chrome', **executable_path, headless=False)

def scrape ():
#scrape NASA Mars News Site to collect the information
    browser = init_browser()
    mars_data = {}

    nasa_url = 'https://mars.nasa.gov/news/'
    browser.visit(nasa_url)
    time.sleep(1)
    nasa_html = browser.html
    nasa_soup = bs(nasa_html, 'html.parser')

    news_list = nasa_soup.find('ul', class_='item_list')
    first_item = news_list.find('li', class_='slide')
    nasa_headline = first_item.find('div', class_='content_title').text
    nasa_teaser = first_item.find('div', class_='article_teaser_body').text
    mars_data["nasa_headline"] = nasa_headline
    mars_data["nasa_teaser"] = nasa_teaser

# visit the JPL website and scrape the featured image
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    time.sleep(1)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1)
    try:
        expand = browser.find_by_css('a.fancybox-expand')
        expand.click()
        time.sleep(1)

        jpl_html = browser.html
        jpl_soup = bs(jpl_html, 'html.parser')

        img_relative = jpl_soup.find('img', class_='fancybox-image')['src']
        image_path = f'https://www.jpl.nasa.gov{img_relative}'
        mars_data["feature_image_src"] = image_path
    except ElementNotVisibleException:
        image_path = 'https://www.jpl.nasa.gov/spaceimages/images/largesize/PIA22076_hires.jpg'
        mars_data["feature_image_src"] = image_path
        
# visit the mars weather report twitter and scrape the latest tweet
    
    twitter_response = req.get("https://twitter.com/marswxreport?lang=en")
    twitter_soup = bs(twitter_response.text, 'html.parser')
    tweet_containers = twitter_soup.find_all('div', class_="js-tweet-text-container")
    for i in range(10):
        tweets = tweet_containers[i].text
        if "Sol " in tweets:
            mars_weather = tweets
            break
    tweets["weather_summary"] = mars_weather

#Mars Facts....scrape the page to get the facts
    request_mars_space_facts = req.get("https://space-facts.com/mars/")

#Use pandas to scrape html table data and set index and table tittles
    mars_space_table_read = pd.read_html(request_mars_space_facts.text)
    df = mars_space_table_read[0]
    df.columns = ["Facet", "Value"]
    df.set_index("Facet", inplace=True)
    mars_facts = df

#convert new pandas df to html, replace "\n" to get html code
    mars_html = mars_data_df.to_html()
    mars_html.replace('\n', '')
    mars_facts.to_html('fact_table.html')    
    
    mars_facts_html = mars_facts.to_html(header=False, index=False)
    mars_facts["fact_table"] = mars_facts_html

# scrape images of Mars' hemispheres from the USGS site
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemi_dicts = []

    for i in range(1,9,2):
        hemi_dict = {}
        
        browser.visit(mars_hemisphere_url)
        time.sleep(1)
        hemispheres_html = browser.html
        hemispheres_soup = bs(hemispheres_html, 'html.parser')
        hemi_name_links = hemispheres_soup.find_all('a', class_='product-item')
        hemi_name = hemi_name_links[i].text.strip('Enhanced')
        
        detail_links = browser.find_by_css('a.product-item')
        detail_links[i].click()
        time.sleep(1)
        browser.find_link_by_text('Sample').first.click()
        time.sleep(1)
        browser.windows.current = browser.windows[-1]
        hemi_img_html = browser.html
        browser.windows.current = browser.windows[0]
        browser.windows[-1].close()
        
        hemi_img_soup = bs(hemi_img_html, 'html.parser')
        hemi_img_path = hemi_img_soup.find('img')['src']

        hemi_dict['title'] = hemi_name.strip()       
        hemi_dict['img_url'] = hemi_img_path

        hemi_dicts.append(hemi_dict)

    mars_data["hemisphere_imgs"] = hemi_dicts

    browser.quit()

    return mars_data
# importing all dependencies

import time
import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser
from selenium.common.exceptions import ElementNotVisibleException
from urllib.parse import urlsplit


def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

# Scraping different sites to get MARS Data 
def scrape():
    
    browser = init_browser()
    mars_data = {}

    # visit the NASA News site and scrape headlines + Article(teaser)
    nasa_url = 'https://mars.nasa.gov/news/'
    browser.visit(nasa_url)
    time.sleep(1)
    nasa_html = browser.html
    nasa_soup = BeautifulSoup(nasa_html, 'html.parser')

    news_list = nasa_soup.find('ul', class_='item_list')
    first_item = news_list.find('li', class_='slide')
    nasa_headline = first_item.find('div', class_='content_title').text
    nasa_teaser = first_item.find('div', class_='article_teaser_body').text
    mars_data["nasa_headline"] = nasa_headline
    mars_data["nasa_teaser"] = nasa_teaser
    print(nasa_headline, nasa_teaser)

# Get the featured IMaGe
    nasa_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=featured#submit"
    browser.visit(nasa_image)
    time.sleep(2)

    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(nasa_image))
    
    xpath = "//*[@id=\"page\"]/section[3]/div/ul/li[1]/a/div/div[2]/img"

    results = browser.find_by_xpath(xpath)
    img = results[0]
    img.click()
    time.sleep(2)
    
    html_image = browser.html
    soup = BeautifulSoup(html_image, "html.parser")
    img_url = soup.find("img", class_="fancybox-image")["src"]
    full_img_url = base_url + img_url
    mars_data["featured_image"] = full_img_url
    print(full_img_url)
     
    # Visit Mars Weather report (twitter) and scrape the latest tweet
    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_weather_url)
    time.sleep(10)
    mars_weather_html = browser.html
    mars_weather_soup = BeautifulSoup(mars_weather_html, 'html.parser')

    tweet = mars_weather_soup.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
    

    mars_weather = tweet.text

    # Adding the weather to the dictionary
    mars_data["weather_summary"] = mars_weather
    # print(mars_weather)

    # Visit space facts and scrap the mars facts table
    mars_facts_url = 'https://space-facts.com/mars/'
    browser.visit(mars_facts_url)

    # Converting the url to a pandas df
    mars_df = pd.read_html(mars_facts_url)
    mars_facts_df = pd.DataFrame(mars_df[0])
        
    mars_facts_df.columns = ['Facet','Value']
    mars_df_table = mars_facts_df.set_index("Facet")

    mars_html_table = mars_df_table.to_html(classes='marsdata')
    mars_table = mars_html_table.replace('\n', ' ')

    # Add the Mars facts table to the dictionary
    mars_data["fact_table"] = mars_table
    print(mars_table)

    # Scrape images of Mars' hemispheres from the USGS site and append them into a dictionary
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemi_dicts = []

    for i in range(1,9,2):
        hemi_dict = {}
        
        browser.visit(mars_hemisphere_url)
        time.sleep(1)
        hemispheres_html = browser.html
        hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')
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
        
        hemi_img_soup = BeautifulSoup(hemi_img_html, 'html.parser')
        hemi_img_path = hemi_img_soup.find('img')['src']

        hemi_dict['title'] = hemi_name.strip()       
        hemi_dict['img_url'] = hemi_img_path

        hemi_dicts.append(hemi_dict)

    mars_data["hemisphere_imgs"] = hemi_dicts
    # print("Got Mars Hemispheres.")
    # print(hemi_dicts)
    return mars_data

    
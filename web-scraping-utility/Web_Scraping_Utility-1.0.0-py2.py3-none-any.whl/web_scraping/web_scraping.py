
# coding: utf-8

# # Web Scraping Utilities Functions

# In[1]:

# Open the chrome driver
from selenium import webdriver
import os
def open_browser(url):
    direc = os.getcwd()
    newpath = os.path.join(direc, 'chromedriver' + "." + 'exe')
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : direc}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(newpath, chrome_options=chrome_options)
    driver.get(url)
    return driver


# In[2]:

# Get the soup Instance
from bs4 import BeautifulSoup
from requests import get


# In[3]:

def get_soup_instance(url):
    resp = get(url)
    if(resp.status_code == 200):
        soup = BeautifulSoup(resp.content, 'lxml')
        return soup
    return False


# In[30]:

# get_ipython().system('jupyter nbconvert --to python web_scraping.ipynb')


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




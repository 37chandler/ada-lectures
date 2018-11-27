# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 21:14:03 2018

@author: JohnC

Pulls RSS information for our cities
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
import datetime
import time
import random
from cl_car_functions import *

#working_dir = "c:\\Users\\JChan\\Dropbox\\Research\\car-buying\\"
working_dir = "c:\\Users\\Administrator\\Dropbox\\Research\\car-buying\\"
db_name = "Data\\car_data.db"

places = ["atlanta","minneapolis","missoula"]
rss_url_start = "https://"
rss_url_end = ".craigslist.org/search/cto"
params = {'format':'rss',
          'query':'subaru',
          's':1}
max_pulls = 30 # max per city

logging.basicConfig(filename="".join([working_dir,"logs\\","rss_pulls.log"]), level=logging.INFO)

logging.info("Starting the RSS pull script: " + str(datetime.datetime.now()))

  
if not logging.getLogger().isEnabledFor(logging.DEBUG) :
  # Wait between 1 and 30 minutes to add some randomness.
  time.sleep(random.uniform(60,30*60))

logging.info("Done waiting to start: " + str(datetime.datetime.now()))
  
with sqlite3.connect(working_dir + db_name) as con :
    cur = con.cursor()
    
    cur.execute("""SELECT DISTINCT post_id
                    FROM rss_pull""")
    
    current_post_ids = set([item[0] for item in cur.fetchall()])
    logging.debug("Total post_ids: " + str(len(current_post_ids)))
    
    total_entries = 0
    for city in places :
      if not logging.getLogger().isEnabledFor(logging.DEBUG) :
        # Wait between 1 and 5 minutes to add some randomness.
        time.sleep(random.uniform(1*60,5*60))

      logging.info("Done waiting. Starting " + city + ": " + str(datetime.datetime.now()))

      city_entries = 0 # items for the city
      city_pulls = 0
      done_with_city = False
      params['s'] = 0
        
      while not done_with_city :
        rss_page = requests.get("".join([rss_url_start,city,rss_url_end]),
                               params=params)
        rss_soup = BeautifulSoup(rss_page.text,"lxml")
        
        city_pulls += 1
        pull_results = process_rss_page(rss_soup,cur,
                                        current_post_ids,
                                        city)
        
        city_entries += pull_results['items_uploaded']
        
        if (pull_results['total_items'] == 0 or
          city_pulls >= max_pulls) :
          done_with_city = True
        else :
          params['s'] += pull_results['total_items']
 
      total_entries += city_entries
      
      logging.info(" ".join(["Just pulled",str(city_entries),"values for",city]))
        
    con.commit()
    logging.info(" ".join(["Total new URLs:",str(total_entries)]))
 
logging.info("Finished RSS Pull: " + str(datetime.datetime.now()) + "\n\n")

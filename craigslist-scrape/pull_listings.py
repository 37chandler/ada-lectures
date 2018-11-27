# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 18:44:08 2018

@author: john

The RSS populator script.

"""

import sqlite3
import logging
import random
import requests
from bs4 import BeautifulSoup
import time
import datetime

from cl_car_functions import *

#working_dir = "c:\\Users\\JChan\\Dropbox\\Research\\car-buying\\"
working_dir = "c:\\Users\\Administrator\\Dropbox\\Research\\car-buying\\"
db_name = "data\\car_data.db"

do_waits = True
# If do_waits then there are a bunch of built-in random waits
# in the script. If not, then we only pull 5 records and 
# don't wait. 

def main() :
  ''' 
    Main handler for the listing page mining script. 
    
    TODO: Add flags if a post is deleted or expired or flagged for removal.
    
  '''

  logging.basicConfig(filename="".join([working_dir,"logs\\","listing_pulls.log"]), 
                      level=logging.INFO)

  logging.info("\n\n")  
  logging.info("Starting the Listing pull script: " + str(datetime.datetime.now()))
  
  if not logging.getLogger().isEnabledFor(logging.DEBUG) :
    skip_rand = random.random()
    
    logging.debug("Will skip this run if skip_rand ({0:.3f}) is under 0.1.".format(skip_rand))
  
    # 10% of the time, skip this hour
    if skip_rand < 0.1 and do_waits :
      logging.info("Bailing on listing scrapes #sneaky.")
      return(0)
    else :
      # Adding this comment to get more visibility into skips
      logging.debug("Didn't skip.")
    
      if do_waits :
        # Wait between 1 and 30 minutes to add some randomness.
        waiting_time = random.uniform(60,10*60)
        logging.info("Waiting for " + str(round(waiting_time,2)))
        time.sleep(waiting_time)

  logging.info("Done waiting to start: " + str(datetime.datetime.now()))

  con = sqlite3.connect(working_dir + db_name) 
  cur = con.cursor()
  
  if do_waits :
    urls = determine_urls(cur)
    #urls = determine_urls(cur,num_to_pull = 35, the_city = "minneapolis")

  else :
    urls = determine_urls(cur,num_to_pull=5)
    
  for the_url in urls :
    update_to_attempted(cur,the_url)
    
    listing_page = requests.get(the_url)
    listing_soup = BeautifulSoup(listing_page.text,"lxml")

    listing_data = process_page(listing_soup)
    
    if listing_data is not None :
        listing_data['url'] = the_url
        write_listing_row(cur,listing_data)
        update_to_processed(cur,the_url)

    if do_waits :
      wait_amt = random.uniform(2,30)
      logging.debug("Waiting for " + str(wait_amt))
      time.sleep(wait_amt)
  
  logging.info(" ".join(["Just filled in",str(len(urls))]))
  con.commit()
  con.close()
  
  return(0)



if __name__ == "__main__":
  # execute only if run as a script
  main()
  logging.info("Finished pulling listing data: " + str(datetime.datetime.now()))


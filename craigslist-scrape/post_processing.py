# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:10:36 2018

@author: john chandler

Holds the post-processing code. Basically, once we've extracted
what we want from the CL page, we store that data. This 
code is everything in Python downstream of that. 

TODO: what about a "make_confidence" in the DB that will let me indicate how
good I feel about that data being accurate? 

"""

import logging
import datetime
import sqlite3

from post_processing_functions import * 

#working_dir = "c:\\Users\\jchan\\Dropbox\\Research\\car-buying\\"
working_dir = "c:\\Users\\Administrator\\Dropbox\\Research\\car-buying\\"

def main() :
  """
    Calls functions that run over the listings
    table each day. 
      * Extract Make. 
      * Extract Model
      * Extract Year
      * Classify as Fishy
  """
  
  # A bunch values needed for this run.   
  makes_model_file = "data\\allMakes.txt"
  
  db_name = "Data\\car_data.db"

  makes_to_use = ["Subaru"]
  models_to_add = {"Subaru":["sti"]}

  # DB Hookup
  con = sqlite3.connect(working_dir + db_name)
  cur = con.cursor()
  
  # get a list of all the make, models and years in the makes_models_file
  mmy = populate_mmy(working_dir, makes_model_file,makes_to_use)
  makes_to_models = populate_make_to_models(mmy, models_to_add)
  
  populate_makes(cur,makes_to_models)

  populate_models(cur,makes_to_models)  

  populate_years(cur,mmy)
  #classify_as_fishy(cur)

  con.commit()
  con.close()


"""
select model, count(*) as cnt
from listing_data
group by model
order by cnt desc
"""

if __name__ == "__main__":
  # execute only if run as a script
  
  # Start logging
  logging.basicConfig(filename="".join([working_dir,"logs\\","listing_processing.log"]), 
                      level=logging.INFO)

  logging.info("Started processing listings." + str(datetime.datetime.now()))
  main()
  logging.info("Finished processing listings." + str(datetime.datetime.now()))

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 21:05:32 2018

@author: john

Holds functions that are used by post-processing.

"""

import json
import sqlite3
from collections import defaultdict
import logging
import re

number_re = re.compile("[0-9]+")
punct_regex = re.compile(r'[^\w\s]')

#############################################################################
#                    Helper functions                                       #
#############################################################################

def populate_mmy(working_dir,
                 make_model_file,
                 makes_to_use) :
  """
    Populates a dictionary make_model_year. 
    Restricted to makes in makes_to_use. 
  """
  
  mm = json.loads(open(working_dir + make_model_file).read())['makes']

  make_model_year = defaultdict(lambda: defaultdict(list))
  
  for item in mm :
    if item['name'] in makes_to_use :
      for mod in item['models'] :
        for yr in mod['years'] :
          make_model_year[item['name'].lower()][mod['name'].lower()].append(yr['year'])

  return(make_model_year)                

def populate_make_to_models(mmy,mods_to_add) :
  '''
    Given our make_model_year dict of lists, this
    creates a dict of sets where words related to models
    are stored. This will make it quick to look for these 
    words in the posting text. 
  '''
  # Let's make a dict of sets of (lowercase) models.
  make2mod = defaultdict(set)

  for make in mmy :
    for mod in mmy[make] :
      make2mod[make.lower()].add(mod.lower())
        
  for make in mods_to_add :
    for mod in mods_to_add[make] :
      make2mod[make.lower()].add(mod.lower())

  return(make2mod)

#############################################################################
#                    Make functions                                         #
#############################################################################

def check_for_other_makes(other_mm) :
  """
    TK
    
    Checks for the presence of a make that *isn't* in our 
    makes_to_use in the listing.
    
  """
  pass

def text_contains_make(text, m2m) :
  """
    checks a body of text for a make. The makes
    are the keys in m2m.
  """
  makes = set([m.lower() for m in m2m])
  text = set([w.lower() for w in text.replace(","," ").split()])
  
  return(len(makes.intersection(text)) > 0) 
  
def extract_make(text, m2m) :
  """
    Extracts a make contained in m2m from text. 
    The makes are the keys in m2m.
  """
  makes = set([m.lower() for m in m2m])
  
  # let's split the text on punctuation and whitespace
  # and drop empty strings. 
  text = set([w.lower() for w in text.replace(","," ").split()])
  # TODO: make splitting smarter by adding more punctuation 
  # and only do it in one place. (Rather than here and above.)
  
  make_words = makes.intersection(text)
  
  if len(make_words) == 1 :
    return(list(make_words)[0]) 
  elif len(make_words) > 1 :
    logging.debug("Multiple make words in  " + text)
    return("-".join(make_words))    
  else :
    logging.debug("We didn't find a make in " + text + "\nBut expected one.")
    return("Make Not Found") 
    
def populate_makes(cur,m2m):
  """
    The principal makes function. Gets the makes we need
    to fill in, tries to find out what make should be listed,
    and does the db update. 
  """
  logging.debug("Entering populate makes.")

  # Get makes we'll need to process
  sql_statement = """
        SELECT url, title_text, posting_body_text, full_title_text 
        FROM listing_data 
        WHERE make IS NULL"""

  cur.execute(sql_statement)
  
  num_null_makes = 0 
  num_makes_found = 0
  
  for results in cur.fetchall() :
    
    num_null_makes += 1
    
    the_url, the_title, the_post, full_title = results
    post_and_title = " ".join([full_title,the_post])
    
    this_make = None
    
    if text_contains_make(the_title,m2m) :
      this_make = extract_make(the_title,m2m)
    elif text_contains_make(post_and_title,m2m) :
      this_make = extract_make(post_and_title,m2m)
      

    if this_make :
      num_makes_found += 1
      
      sql_statement = "".join(["UPDATE listing_data SET make = '",
                                 this_make,
                                 "' WHERE url = '",
                                 the_url,
                                 "'"])
        
      cur.execute(sql_statement)

  logging.info("".join(["Null make listings: ",str(num_null_makes)]))
  logging.info("".join(["Null make listings filled in: ",str(num_makes_found)]))
  logging.debug("Exiting populate makes.")
  

#############################################################################
#                    Functions dealing with models                          #
#############################################################################

def text_contains_model(text, make, m2m) :
  """
    checks a body of text for a model. The models
    are the values in m2m. 
  """
  if make not in m2m :
    logging.debug("Didn't find " + make + " in m2m--leaving.")
    return(None)
  else :
    models = m2m[make]
    
  text = set([w.lower() for w in text.replace(","," ").split()])
  
  return(len(models.intersection(text)) > 0) 
  
def extract_model(text, make, m2m) :
  """
    Extracts a make contained in m2m from text. 
    The makes are the keys in m2m.
  """
  if make not in m2m :
    logging.debug("Didn't find " + make + " in m2m--leaving.")
    return(None)
  else :
    models = m2m[make]
    
  text = set([w.lower() for w in text.replace(","," ").split()])
    
  model_words = models.intersection(text)
  
  if len(model_words) == 0 :
    logging.debug("Didn't find a model in " + " ".join(text) + "\n")
    return(None)    
  elif len(model_words) in [1,2] :
    return("-".join(sorted(model_words)))
  else :
    logging.debug("Got more than 2 model words in " + " ".join(text) + "\n")   
    return("-".join(sorted(model_words)))
  

def populate_models(cur,m2m):
  """
    The principal makes function. Gets the makes we need
    to fill in, tries to find out what make should be listed,
    and does the db update. 
  """
  logging.debug("Entering populate_models.")

  # Get makes we'll need to process
  sql_statement = """
        SELECT make, 
               url, 
               title_text, 
               posting_body_text, 
               full_title_text 
        FROM listing_data 
        WHERE make is not NULL and model IS NULL"""

  cur.execute(sql_statement)
  
  num_null_models = 0 
  num_models_found = 0
  
  for results in cur.fetchall() :
    
    num_null_models += 1
    
    make, the_url, the_title, the_post, full_title = results
    post_and_title = " ".join([full_title,the_post])
    
    this_model = None
    
    if text_contains_model(the_title,make, m2m) :
      this_model = extract_model(the_title,make,m2m)
    elif text_contains_model(post_and_title,make,m2m) :
      this_model = extract_model(post_and_title,make,m2m)
      
    if this_model :
      num_models_found += 1
      
      sql_statement = "".join(["UPDATE listing_data SET model = '",
                                 this_model,
                                 "' WHERE url = '",
                                 the_url,
                                 "'"])
        
      cur.execute(sql_statement)

  logging.info("".join(["Null model listings: ",str(num_null_models)]))
  logging.info("".join(["Null model listings filled in: ",
                         str(num_models_found)]))
  logging.debug("Exiting populate_model.")



#############################################################################
#                    Functions dealing with years                           #
#############################################################################

def get_title_year(title,years,abbrs2yr) :
  """
    Given a set of years, is that year in the title
    once we cut down to numbers and split? Returns
    a year or None.
  """
  
  title = title.replace("'","")
  title = title.replace("."," ")
  title = title.replace(","," ")

  # TODO: people have stuff like 20o8. Fix? 
  
  nums = [int(s) for s in title.split() if s.isdigit()]
  nums = [str(n).zfill(2) for n in nums]
  
  for num in nums :
    if num in years :
      return(num)
      
  # Didn't find a year. Let's look for a two-digit year
  for num in nums :
    if num in abbrs2yr :
      return(abbrs2yr[num])
  
  return(None)
    

def get_post_year(post,years,abbrs2yr) :
  """ Extract year(s) from posts. This is a tall order, 
      since people put a lot of garbage in here. This includes
      things like the year they got new tires or whatever. 
      I think we'll find everything that looks like a year and 
      return a string with YYYY, YYYY, YYYY for those that 
      more than one year."""
    
  found_nums = set()
  
  post = punct_regex.sub('',post)
  
  pieces = set(post.split())  

  for num in pieces.intersection(years) :
    found_nums.add(num)

  # Didn't find a year. Let's look for a two-digit year
  for num in pieces.intersection(abbrs2yr.keys()) :
    found_nums.add(abbrs2yr[num])
  
  if found_nums :
    return(",".join([str(num) for num in found_nums]))
  else :
    return(None)  
  


def populate_years(cur,mmy):
  """
    Given a DB connection and the mmy[make][model] = [years] dictionary,
    populate the year field in the DB. 
  """
  logging.debug("Entering populate_years.")
  
  years_to_consider = set()
  abbr_to_year = dict()

  for make in mmy :
    for model in mmy[make] :
      for yr in mmy[make][model] :
        years_to_consider.add(str(yr))
        
        abbr_to_year[str(yr)[2:]] = yr

  # Get makes we'll need to process
  sql_statement = """
        SELECT year, 
               url, 
               title_text, 
               posting_body_text, 
               full_title_text 
        FROM listing_data 
        WHERE year is NULL"""

  cur.execute(sql_statement)
  
  num_null_years = 0 
  num_years_found = 0
  
  for results in cur.fetchall() :
    
    num_null_years += 1
    
    year, the_url, the_title, the_post, full_title = results
    
    # Hierarchy will be year in  title, then post
    
    this_year = get_title_year(the_title,
                               years_to_consider,
                               abbr_to_year)
    
    if not this_year :
      this_year = get_post_year(the_post,
                                years_to_consider,
                                abbr_to_year) 
      
    if this_year :
    
      num_years_found += 1
      
      sql_statement = "".join(["UPDATE listing_data SET year = '",
                                 str(this_year),
                                 "' WHERE url = '",
                                 the_url,
                                 "'"])
        
      cur.execute(sql_statement)

  logging.info("".join(["Null year listings: ",str(num_null_years)]))
  logging.info("".join(["Null model listings filled in: ",
                         str(num_years_found)]))
  logging.debug("Exiting populate_model.")


#############################################################################
#             Other funtions that aren't "helpers"                          #
#############################################################################


def classify_as_fishy(cur):
  """
    TK
  """
  pass




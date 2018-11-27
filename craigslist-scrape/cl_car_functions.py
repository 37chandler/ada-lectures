"""
Created on Mon Mar 05 17:14:03 2018

@author: JohnC

Holds functions related to pulling car information from CL.

"""

import re
import sqlite3
import logging
import datetime
import time
import random
import operator

quote_match = re.compile(r'\"(.+)\"')

# TODO: 
# Check out https://missoula.craigslist.org/cto/d/02-subaru-impreza-wrx-wagon/6505745275.html
# Has a first entry under attr group that has actual year/make/model
#
# TODO: run check to figure out if we're getting duplicates. First 
# question: do reposts end up with new URLs?
#
# TODO: need to flag some of these for inspection. The three hyphens, for 
# instance, but also weird make/models.

def get_areas(soup) :
  """ Given a souped page, returns the geo values in a 
    dictionary with the values associated with the 
    SQL column names. Geo values are  
    crumb_area, crumb_subarea."""
  
  area = subarea = None
  
  holder = soup.find_all("li",{"class":"crumb area"})
  if len(holder) > 0 :
    for idx, element in enumerate(holder[0]) :
      if idx == 1 :
        area = element.find("a").string

  holder = soup.find_all("li",{"class":"crumb subarea"})
  if len(holder) > 0 :
    for idx, element in enumerate(holder[0]) :
      if idx == 1 :
        subarea = element.find("a").string

  return({"crumb_subarea":subarea,
      "crumb_area":area})    
  
  
  
def get_vehicle_info(soup) :
  ''' The hard worker. Given soup, returns a dictionary with 
    most of the vehicle info. vin, cond, cyl, drive,
    fuel, odometer, paint_color, size, trans, type.
  '''
  car_text = soup.find_all("p", {"class":"attrgroup"})[1]
  # Set all values to None to start
  vin = cond = cyl = drive = fuel = None
  odometer = title_status = trans = None
  color = size = type_val = None

  for item in car_text.find_all("span") :
    if "VIN" in str(item) :
      vin = item.b.string
    elif "condition" in str(item) :
      cond = item.b.string
    elif "cylinders" in str(item) :
      cyl = item.b.string 
    elif "drive" in str(item) :
      drive = item.b.string 
    elif "fuel" in str(item) :
      fuel = item.b.string 
    elif "odometer" in str(item) :
      odometer = item.b.string 
    elif "title status" in str(item) :
      title_status = item.b.string 
    elif "transmission" in str(item) :
      trans = item.b.string 
    elif "paint color" in str(item) :
      color = item.b.string 
    elif "size" in str(item) :
      size = item.b.string
    elif "type" in str(item) :
      type_val = item.b.string
    
  ret_d = {"vin":vin,
       "condition":cond,
       "cylinders":cyl,
       "drive":drive,
       "fuel":fuel,
       "odometer":odometer,
       "title_status":title_status,
       "transmission":trans,
       "paint_color":color,
       "size":size,
       "type":type_val}
  
  # TODO: need type?

  return(ret_d)
  
  
  
  
def get_page_elements(soup) :
  ''' Getting elements of the page that 
    *should* be mostly straightforward:
    post_id, listing_name, posting_body_text,
    title_text, posting_dt, update_dt 
    price
  '''
  
  # post-id
  post_id = None
  for item in soup.find_all("p",{"class":"postinginfo"}) :
    if "post" in str(item.string) :
      post_id = item.string.split(":")[1]
      post_id = post_id.strip()
  
  # listing_name
  # TODO: Not sure what this is. I put it in the 
  # db design, but don't know what it means. Leaving 
  # it in for now in the hopes that I'll remember
  # what I was seeing.
  listing_name = None
  
  # posting_body_text
  posting_body_text = soup.find_all("section",{"id":"postingbody"})[0].text.strip() 
  
  # title_text
  full_title_text = soup.find_all("span",{"class":"postingtitletext"})[0].text.split("\n")
  full_title_text = [a for a in full_title_text if len(a) > 0]  
  
  # attempt at actual title. Is hyphen split reliable?
  title_text = full_title_text[0].split("-")[0].strip()
  
  # grab price and location
  price = location = None
  hyphens = full_title_text[0].count("-")
  
  if hyphens > 0 :    
    # This is tricky. It's possible to have
    # multiple hyphens in the title text. 
    
    if hyphens == 1 :
      price_spot = 1
    elif hyphens == 2 :
      price_spot = 2
    else :
      logging.info(" ".join(["We found",str(hyphens),
                      "in this title:",
                      full_title_text[0]]))
      price_spot = hyphens # hope for the best
    
    
    price_loc_part = full_title_text[0].split("-")[price_spot].strip()
    price = price_loc_part.split("(")[0].strip()
    price = price.replace("$","")
    # TODO: add error checking and logging. Also, 
    # this could be separated out of the pull itself.
  
    # location: the place listed in the title
    if "(" in price_loc_part :
      location = price_loc_part.split("(")[1].strip()
      location = location.replace(")","")
  
  full_title_text = "".join(full_title_text) 
  # For now we're storing this so we can figure out if we're screwing it up.
  
  # times
  posting_dt = update_dt = None
  
  for item in soup.find_all("p",{"class":"postinginfo reveal"}) :
    if "posted:" in item.text :
      holder = item.find_all("time")[0]
      posting_dt = holder.attrs['datetime']
    elif "updated:" in item.text :
      holder = item.find_all("time")[0]
      update_dt = holder.attrs['datetime']  
      
  # Num images
  holder = soup.find_all("div",{"id":"thumbs"})
  if len(holder) > 0 :
    num_images = len(holder[0].find_all("a"))    
  else :
    num_images = 0

  ret_d = {"post_id":post_id,
       "listing_name":listing_name,
       "posting_body_text":posting_body_text,
       "full_title_text":full_title_text,
       "title_text":title_text,
       "posting_dt":posting_dt,
       "update_dt":update_dt,
       "price":price,
       "location":location,
       "num_images":num_images}
  
  return(ret_d)
  
  
  
def process_page(soup) :
  ''' Once an RSS page has been requested, this extracts all the 
    page elements. Uses underlying functions for the elements.'''
  
  if page_gone(soup) :
    # TODO: update rss_pull list with
    # notification that this page 
    # has expired, along with a time stamp.
    # Also, add something checking (once) for
    # this expiration.
    
    return(None)
  else :  
    results = get_areas(soup)
  
    for k,v in get_vehicle_info(soup).items() :
      results[k] = v
  
    for k,v in get_page_elements(soup).items() :
      results[k] = v
  
    return(results)

def update_to_processed(cur,url) :
  '''
    Changes the 0 to 1 in rss_pull processed column.
  '''
  
  sql_statement = "".join([
      """UPDATE rss_pull 
         SET processed = 1
         WHERE url = '""",
         url,
         "'"])
  cur.execute(sql_statement)
  
def update_to_attempted(cur,url) :
  '''
    Changes the 0 to 1 in rss_pull attempted column.
    Prevents us from constantly re-pulling deleted 
    posts.
  '''
  
  sql_statement = "".join([
      """UPDATE rss_pull 
         SET attempted = 1
         WHERE url = '""",
         url,
         "'"])
         
  cur.execute(sql_statement)


def write_listing_row(cur,listing_data) :
  ''' 
    Given a cursor and the listing data,
    this function prepares the data for import
    and does the insert.
  '''
  
  input_line = [listing_data['post_id'],
                listing_data['listing_name'],
                listing_data['vin'],
                listing_data['condition'],
                listing_data['cylinders'],
                listing_data['drive'],
                listing_data['fuel'],
                listing_data['odometer'],
                listing_data['title_status'],
                listing_data['paint_color'],
                listing_data['size'],
                listing_data['transmission'],
                listing_data['type'],
                listing_data['posting_body_text'],
                listing_data['title_text'],
                listing_data['full_title_text'],
                listing_data['price'],
                listing_data['location'],
                listing_data['url'],
                listing_data['posting_dt'],
                listing_data['update_dt'],
                listing_data['crumb_area'],
                listing_data['crumb_subarea'],
                listing_data['num_images'],
                str(datetime.datetime.now())]
          
    
  cur.execute('''INSERT INTO listing_data (
                 post_id, listing_name, vin, 
                 condition, cylinders, drive, fuel,
                 odometer, title_status, paint_color,
                 size, transmission, type, posting_body_text,
                 title_text, full_title_text,
                 price, location, url, 
                 posting_dt, update_dt, crumb_area,
                 crumb_subarea, num_images, processed_time)
                 VALUES
                 (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                  ?,?,?,?,?,?,?,?,?)''',
                  input_line)

  
  return(0)


def page_gone(soup) :
  ''' Given the soup of a page, return a boolean
    indicating that the page is gone. We
    flag removed vs expired, but don't pass that back out.'''
    
  # TODO: There are more ways this can be true. Expired, 
  # removed, flagged for removal. Should return 
  # {'page_gone':T/F, 
  #  'type':['removed','expired','flagged',None]}
  # 
  # Is removed the same as deleted? 
  
  post_not_found = soup.find("div",{"class":"post-not-found"})
  post_removed = soup.find("span",{"id":"has_been_removed"})

  if post_not_found is not None :
    # was expired, I think
    return(True)
  elif post_removed is not None :
    # was removed
    return(True)
  else :
    return(False)
  
  
def determine_urls(cur,
                   num_to_pull = None,
                   the_city=None) :
  '''
     Determine the URLs to gather data from. 
     
     First, pick a city. Then grab N URLs from
     that city. We'll assume that we're running this 
     every hour during normal human hours. And
     maybe taking some time off. 
     
  '''
  
  # If the number of unpulled is higher than 
  # this number, we'll randomize. Otherwise
  # we'll just do what we have. 
  cutoff_for_random = 30
  
  # TODO: need to add checks to make sure we're
  # not falling woefully behind in some city. It 
  # seems like we could run into a situation where
  # Missoula doesn't get pulled that often. 
  # 
  # TODO: Also, probably need to force us to pull
  # anything that's older than about 36 hours...
  
  if the_city is None :
    cur.execute(''' SELECT city, count(*) as cnt
                    FROM rss_pull
                    WHERE attempted = 0
                    GROUP BY city''')
    
    unprocessed = {}
    
    for cty, cnt in cur.fetchall() :
      unprocessed[cty] = cnt
      
    if not unprocessed :
      # Nothing unprocessed! That might be bad.
      logging.info("Nothing unprocessed in rss_pull. Is that expected?")
      return([])
    else :  
      the_city = max(unprocessed.items(), 
                     key=operator.itemgetter(1))[0]  
      
      logging.info("".join(["Pulling for ",
                            the_city,
                            ", which has ",
                            str(unprocessed[the_city]),
                            " unprocessed URLs."]))

  if num_to_pull is None :
    if unprocessed[the_city] < cutoff_for_random :
      num_to_pull = unprocessed[the_city]
    else :
      ub = 1.5*unprocessed[the_city]
      lb = max(cutoff_for_random*2/3,ub//2)
    
      num_to_pull = round(random.uniform(lb,ub),0)
      num_to_pull = min(num_to_pull, unprocessed[the_city])
      

  logging.info("".join(["Going to pull ",
                        str(num_to_pull), 
                        " records for ",
                        the_city, "."]))
                        
  logging.debug("".join(["num_to_pull=",
                         str(num_to_pull),
                         "\nthe_city=",
                         the_city,
                         "\nunprocessed=",
                         str(unprocessed)]))

                         
  sql_statement = "".join(["""
               SELECT url
               FROM rss_pull
               WHERE processed = 0 
               and city = '""", 
               the_city, 
               "' ORDER BY random() LIMIT ", 
               str(num_to_pull)])
     
  logging.debug("SQL Statement: " + sql_statement + "\n")
  cur.execute(sql_statement)
  
  return([u[0] for u in cur.fetchall()])

######################################################################  
#                    RSS RELATED CODE                                #  
######################################################################  

def process_rss_page(rss_soup, cur, current_ids, city) :
  ''' Given an RSS page, a cursor and the current post 
      IDs that we've got in the DB, this code
      1. Pulls the items we need from the RSS page.
      2. Uploads them to the DB if they're not in there.
      3. Returns a dictionary with the number pulled and
         the number uploaded. '''
    
  total_items = 0
  items_uploaded = 0
    
  for item in rss_soup.find_all(b"rdf:li") :
    total_items += 1

    the_url = quote_match.findall(str(item))[0]
    post_id = the_url.split("/")[-1].replace(".html","")

    if post_id not in current_ids :
      new_row = (city,
                 the_url,
                 post_id,
                 0, # not processed yet
                 str(datetime.date.today()),
                 0) # also not attempted yet
      
      cur.execute('''INSERT INTO rss_pull (
                      city, url, post_id, processed, pull_date, attempted)
                    VALUES (?,?,?,?,?,?)''',new_row)
      
      items_uploaded += 1

  return({'total_items':total_items,
          'items_uploaded':items_uploaded})

  
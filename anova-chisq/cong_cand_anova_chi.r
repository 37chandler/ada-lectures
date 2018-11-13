# A file to get you started playing
# around with the congressional candidate
# data. 

library(dplyr)
library(DBI)
library(ggplot2)
library(scales)

path.to.db <- "C:\\Users\\jchan\\Dropbox\\Teaching\\AppliedDataAnalytics\\ada-master\\congressional-candidates\\"
db.name <- "congressional_data.db"

candidate.data.table.name <- "candidate_data"

con <- dbConnect(RSQLite::SQLite(), dbname = paste0(path.to.db,db.name))
cand.tbl <- tbl(con,
                candidate.data.table.name)

# Let's pull candidate name and some of the key fields 
# into a data.frame

d <- cand.tbl %>% 
  select(candidate, district,
         party, age, gender) %>% 
  collect

Hmisc::describe(d)

# What are the parties? 
sort(table(d$party))

# Might need to cut this down for analysis. 




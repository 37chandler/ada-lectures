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
         party, age, gender,
         income,region,
         white_non_hispanic, 
         hispanic, 
         black) %>% 
  collect

Hmisc::describe(d)

# What are the parties? 
sort(table(d$party))

# Might need to cut this down for analysis. 

two.party <- d %>% 
  filter(party %in% c("Democratic","Republican","Libertarian"))

party.gender <- 
  chisq.test(x=two.party$party,
           y=two.party$gender)

residuals(party.gender)


chisq.test(x=two.party$district,
           y=two.party$party)


anova(lm(income ~ party,
         data=d,
         subset=(party %in% c("Democratic",
                              "Republican") &
                   !is.na(income))))


anova(lm(age ~ party,
         data=d,
         subset=(party %in% c("Democratic",
                              "Republican",
                              "Libertarian"))))


library(dplyr)
library(magrittr)
library(tibble)
library(tidyr)
library(data.table) # for fread
library(lubridate)

working.dir <- "C:\\Users\\jchan\\Dropbox\\Teaching\\2016_Fall\\ADA\\Topics\\dplyr\\"
input.file <- "20161025_headline_word_count.txt"

d <- as_data_frame(fread(paste0(working.dir,input.file)))

d <- as_data_frame(d)

print(d)

filter(d,paper=="Missoulian",date=="2016-09-21")

filter(d,paper=="Missoulian"|date=="2016-09-21")

arrange(d,count)
arrange(d,desc(count))
arrange(d,paper,desc(count))

select(d,count)
select(d,count,paper)

mutate(d,
       hl_year = year(date),
       hl_month = month(date))

summarise(d,sum(count))
summarise(group_by(d,paper),sum(count))

d %>% 
  filter("2016-06-01" <= date, 
         date < "2016-09-01") %>% 
  group_by(paper) %>%
  summarise(words = sum(count)) %>% 
  arrange(desc(words))

# Word count.
# Let's get top words from the missoulian
top.word <- d %>% 
  filter(paper=="Missoulian") %>% 
  group_by(word) %>% 
  summarise(count=sum(count))




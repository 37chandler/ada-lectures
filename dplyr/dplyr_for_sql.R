# You might need to run this:
# install.packages("DBI","RSQLite","reshape2","ggplot2","scales")


library(dplyr)
library(DBI)
library(reshape2)
library(ggplot2)
library(scales)

# These next lines will need to be modified for your DB
# and system.
path.to.db <- "C:\\Users\\jchan\\Dropbox\\Teaching\\2018_Fall\\AppliedData\\week_10\\"
db.name <- "Anthony_Layton_WedgeDB.db"
owner.sales.table.name <- "Sales_yb_Owner_by_Year_by_Month"


con <- dbConnect(RSQLite::SQLite(), dbname = paste0(path.to.db,db.name))
owner.tbl <- tbl(con,
                 owner.sales.table.name)

owner.tbl %>% 
  head

# What was the total owner sales in 2015? 2016?
owner.tbl %>% 
  filter(card_no!=3) %>% 
  group_by(year) %>% 
  summarize(sum(spend,na.rm=T))

# For fun let's do owner and non-owner by year and plot it
owner.tbl %>% 
  mutate(is_owner = if_else(card_no==3,"no","yes")) %>%  
  group_by(year,is_owner) %>% 
  summarize(total_spend=sum(spend,na.rm=T)) %>% 
  filter(year!=2017) %>% #drop partial year
  ggplot(aes(x=year,y=total_spend,
             group=is_owner,color=is_owner)) +
  geom_line() + 
  theme_minimal() + 
  scale_y_continuous(label=dollar) +
  labs(x="",
       y="Spend",
       title="Spending by Year for Owners and Non-Owners")

# one other trick. Imagine you wanted my spending.
d <- owner.tbl %>% 
  filter(card_no==18736)

# how many rows are there?
nrow(d)

# this is NA because dplyr doesn't pull the data 
# over to R unless you explicitly ask for it. This
# "lazy evaluation" is useful, but tricky when you
# first encounter it.
d <- owner.tbl %>% 
  filter(card_no==18736) %>% 
  collect

nrow(d)


# Now your turn. Knock out these other questions. No 
# need to do any plotting. 

# Which owner had the 50th highest spend in 2015? How much did they spend in 2016? 
spend.2015 <- owner.tbl %>% 
  filter(year==2015,card_no != 3) %>% 
  group_by(card_no) %>% 
  summarize(total_spend = sum(spend)) %>% 
  arrange(desc(total_spend)) %>% 
  collect

spend.2015[50,]

20596

owner.tbl %>% 
  filter(year==2016,card_no == 20596) %>% 
  group_by(card_no) %>% 
  summarize(total_spend = sum(spend)) 
  # 11067

# How many owners spent at least $1000 in 2015 and spent $0 in 2016?
spend.2015 <- owner.tbl %>% 
  filter(year==2015,card_no != 3) %>% 
  group_by(card_no) %>% 
  summarize(total_spend = sum(spend,na.rm=T)) %>% 
  filter(total_spend >= 1000) %>% 
  collect

spend.2016 <- owner.tbl %>% 
  filter(year==2016,card_no != 3) %>% 
  group_by(card_no) %>% 
  summarize(total_spend = sum(spend,na.rm=T)) %>% 
  filter(total_spend != 0) %>% 
  collect

spend.2015 %>% 
  filter(!(card_no %in% spend.2016$card_no))

# What product had the largest increase in sales (in raw dollars) between 2015 and 2016? 

prod.tbl <- tbl(con,
                 "Sales_by_Product_by_Year_by_Month")

d <- prod.tbl %>% 
  filter(year==2015) %>% 
  group_by(description) %>% 
  summarise(total_spend = sum(spend)) %>% 
  collect

d <- d %>% 
  left_join(prod.tbl %>% 
              filter(year==2016) %>% 
              group_by(description) %>% 
              summarise(total_spend = sum(spend)) %>% 
              collect,
            by="description")

names(d) <- c("description","spend.2015","spend.2016")

d <- d %>% 
  mutate(increase = spend.2016 - spend.2015) %>% 
  arrange(desc(increase)) 

ggplot(d,
       aes(x=increase)) + 
  geom_density()+
  theme_minimal() +
  scale_x_continuous(limits=c(-5000,5000),
                     label=dollar)




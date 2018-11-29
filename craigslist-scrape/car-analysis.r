library(dplyr)
library(reshape2)
library(ggplot2)
library(scales)
library(lubridate)

library(DBI)
library(RSQLite)


working.dir <- "C:\\Users\\jchan\\Dropbox\\Research\\car-buying\\"
analysis.folder <- "analysis\\"
data.folder <- "data\\"

db.name <- "car_data.db"

con <- dbConnect(SQLite(), 
                 dbname = paste0(working.dir,data.folder,db.name))

d <- tbl(con,"listing_data")

# let's do a basic model for outbacks and foresters

md <- d %>% 
  filter(!is.na(price),
         !is.na(year),
         !is.na(odometer),
         title_status == "clean",
         !is.na(model)) %>% 
  select(url,location,
         odometer,
         title_text,
         posting_body_text,
         crumb_area,
         posting_dt,
         num_images,
         model,
         year,
         price) %>% 
  collect

md <- md %>% 
  mutate(posting_dt = ymd_hms(posting_dt),
         year_chars = nchar(year))
  
# for now, dropping bad years
md <- md %>% 
  filter(year_chars==4) %>% 
  mutate(year = as.numeric(year),
         price = as.numeric(price),
         odometer = as.numeric(odometer)) %>% 
  mutate(age = 2019 - year) 

md$odometer[md$odometer < 1000] <- md$odometer[md$odometer < 1000]*1000


# Let's look at some relationships
ggplot(md %>% 
         filter(model %in% c("outback","legacy","forester")),
       aes(x=age,y=price, group=model,color=model)) +
  geom_point(position=position_jitter()) + 
  stat_smooth() +
  facet_wrap(~crumb_area,ncol=1) + 
  theme_minimal() + 
  scale_y_continuous(label=dollar) + 
  scale_x_log10()


ggplot(md %>% 
         filter(model %in% c("outback","legacy","forester")),
       aes(x=odometer,y=price, group=model,color=model)) +
  geom_point(position=position_jitter()) + 
  stat_smooth() +
  theme_minimal() + 
  facet_wrap(~crumb_area,ncol=1) + 
  scale_y_continuous(label=dollar) + 
  scale_x_continuous(limits = c(20000,300000),
                     label=comma)

md %>% 
  filter(price > 50000)

# I'm interested in price distributions by city for the most popular
# models. First, let's figure out what those are.
model.name <- "wrx"

md %>% 
  filter(grepl(model.name,model)) %>% 
  filter(model != model.name) %>% 
  pull(model) %>% 
  table %>% 
  sort

# forester-xt is like forester
# wow, lots of outback. impreza-outback, legacy-outback
#    outback-xt
# wrx: impreza-wrx, sti-wrx

sort(table(md$model))

models.to.use <- c("outback","forester","legacy",
                   "impreza","wrx","impreza-wrx",
                   "forester-xt")

md.1 <- md %>% 
  filter(model %in% models.to.use)


lm.1 <- lm(price ~ model * I(log(odometer)) +
             model * age + model*crumb_area + 
             crumb_area*age,
           data=md.1)

summary(lm.1)
anova(lm.1)

md.1$pred_price <- predict(lm.1,md.1)

mso.nd <- md.1 %>% 
  mutate(crumb_area = "missoula")

md.1 <- md.1 %>% 
  mutate(mso_pred_price = predict(lm.1,mso.nd),
         resids = price - mso_pred_price,
         mso_resid = price - mso_pred_price)




md.1 %>% 
  filter(posting_dt > today() - dweeks(3),
         crumb_area == "minneapolis") %>% 
  select(-posting_body_text) %>% 
  arrange(desc(mso_resid)) %>% 
  #filter(price > 10000) %>% 
  #filter(title_text != "2010 SUBARU FORESTER XT LTD AWD MOONROOF VERY CLEAN!") %>% 
  tail(n=10) %>% 
  data.frame

# https://minneapolis.craigslist.org/dak/cto/d/2008-subaru-outback-brand-new/6666203692.html
# https://minneapolis.craigslist.org/ank/cto/d/2010-subaru-forester-xt-ltd/6668849418.html


# maybe we should look at sales prices in missoula. 
ggplot(md %>% 
         filter(crumb_area=="missoula",
                model %in% models.to.use) %>% 
         mutate(model = reorder(model,price,median)),
       aes(y=price,x=model)) + 
  geom_boxplot() + 
  coord_flip() + 
  theme_minimal() + 
  scale_y_continuous(label=dollar)




predict(lm.1,
        newdata=data.frame(model="outback",
                           odometer=257000,
                           age = 14,
#                           crumb_area="minneapolis"),
                            crumb_area="missoula"),
        se.fit=T,
        interval="confidence",
#        interval="prediction",
        level=0.89,
        type="response")
# Was 4995 at car dealership near Dollar



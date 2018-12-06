
library(dplyr)
library(ggplot2)
library(scales)
library(broom)
library(readr)


working.dir <- "C:\\Users\\jchan\\Dropbox\\Teaching\\AppliedDataAnalytics\\ada-master\\logistic-regression\\"
input.data.file <- "trip_scoring_data.txt"

d <- read_tsv(paste0(working.dir,input.data.file))
d <- d %>% unique

client.count <- d %>% 
  count(client) %>% 
  filter(n > 300)

d <- d %>% 
  filter(client %in% client.count$client)


glm.1 <- glm(rebooked ~ mean_leading_days + client,d,family="binomial")
glm.1.1 <- glm(rebooked ~ mean_leading_days * client,d,family="binomial")


summary(glm.1)

anova(glm(rebooked ~ client + client_location,data=d,family="binomial"))

d <- d %>% 
  mutate(alt_domain = if_else(domain=="gmail.com","gmail","other"))



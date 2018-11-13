
library(ggplot2)
library(scales)
library(dplyr)
library(readr)

d <- read_tsv("hamlet_scores.txt")

ggplot(d,
       aes(x=word,y=score)) + 
  geom_line() + 
  theme_bw() + 
  scale_x_continuous(label=comma) + 
  labs(x="Word Position in Hamlet",
       y="Running Sentiment Score",
       title="Sentiment of Hamlet\nOver the Course of the Play") + 
  stat_smooth(se=F,col="red")




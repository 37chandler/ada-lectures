
# Here's a PCA on some Wedge Data. Give 
# this a look. Can you explain what's going 
# on here? 


library(dplyr)
library(ggplot2)
library(reshape2)
library(scales)

d <- readr::read_tsv("owner_level_top_prod_sales.txt")

pca1 <- prcomp(d[,-1])

for.plot <- data.frame(sd=pca1$sdev)
for.plot <- for.plot %>% 
  mutate(eigs=sd^2) %>% 
  mutate(cume.var = cumsum(eigs/sum(eigs)),
         id=1:n())

names(for.plot) <- c("Standard Deviation","eigs",
                     "Cumulative Variance","id")

for.plot <- melt(for.plot,
                 id.vars = "id")

ggplot(for.plot %>% filter(variable != "eigs"),
       aes(x=id,y=value)) +
  geom_line() + 
  facet_grid(variable ~ .,
             scales="free") + 
  theme_bw() + 
  labs(y="Variance",
       x="Component Number")

sort(pca1$rotation[,1],decreasing = T)[1:30]
sort(pca1$rotation[,1],decreasing = F)[1:30]

sort(pca1$rotation[,2],decreasing = T)[1:15]
sort(pca1$rotation[,2],decreasing = F)[1:15]

sort(pca1$rotation[,3],decreasing = T)[1:15]
sort(pca1$rotation[,3],decreasing = F)[1:15]



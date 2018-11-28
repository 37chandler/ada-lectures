
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

sort(pca1$rotation[,4],decreasing = T)[1:15]
sort(pca1$rotation[,4],decreasing = F)[1:15]

# Let's build derived variables from these components. 

# first, let's illustrate the idea.
pc1.loadings <- pca1$rotation[,1] # loadings on first PC

# Owner 19682 spent a lot ($35519.11), Owner 49219 spent very little ($3.08). 
# Let's look at their scores on PCA 1
as.numeric(d[d$owner=="19682",2:1001]) %*% pc1.loadings

# %*% is matrix multiplication in R

as.numeric(d[d$owner=="49219",2:1001]) %*% pc1.loadings

# we can do this en masse and add columns to d
# based on the PCs

num.pcs <- 5

for(i in 1:num.pcs) { 
  col.name <- paste0("score_PC",i)
  
  d[,col.name] <- as.matrix(d[,2:1001]) %*% pca1$rotation[,i]
}

# Let's do a plot of PC3, which looks like "fancy" vs PC4 which seemed to
# differentiate heavy meat eaters

ggplot(d,
       aes(x=score_PC3,y=score_PC4)) + 
  geom_point(alpha=0.2) + 
  theme_minimal()

# Interesting, some crazy outlier there. Let's look at them
d %>% 
  filter(score_PC3 > 6000 | score_PC4 > 2000) %>% 
  select(owner)

d %>% 
  filter(owner==11043) %>% 
  melt(id.vars="owner") %>% 
  arrange(value) %>% 
  tail(n=20)
# this person spent a *ton* on fancy things. They
# might be driving most of this behavior.

d %>% 
  filter(owner==12584) %>% 
  melt(id.vars="owner") %>% 
  arrange(value) %>% 
  tail(n=20)
# This person spent a *ton* on greens and juicer-type stuff.

# we could remove some of these extreme values 
# (I wouldn't call them "outliers") and maybe 
# get better a better PCA. right now we're pulling off
# just a handful of people with each dimension. 

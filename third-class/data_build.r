# used to build data for student exercises in ADA

library(dplyr)
library(readr)

data(iris)

output.dir <- "C:\\Users\\jchan\\Dropbox\\Teaching\\AppliedDataAnalytics\\ada-master\\third-class\\data\\"

# header, tab
write.table(iris,
            paste0(output.dir,"file1.csv"),
            quote = TRUE,
            sep="\t",
            na="NA",
            row.names=F,
            col.names=T)


# header csv
write.table(iris,
            paste0(output.dir,"file2.csv"),
            quote = TRUE,
            sep=",",
            na="NA",
            row.names=F,
            col.names=T)

# comma, no header
write.table(iris,
            paste0(output.dir,"file3.csv"),
            quote = TRUE,
            sep=",",
            na="NA",
            row.names=F,
            col.names=F)

# semi-colon,  header
write.table(iris,
            paste0(output.dir,"file4.csv"),
            quote = TRUE,
            sep=";",
            na="NA",
            row.names=F,
            col.names=F)


# Now add in some missing values
iris.with.na <- iris
set.seed(20180917)

for(i in 1:nrow(iris)) {
  for(j in 1:ncol(iris)) {
    this.rand <- runif(1)
    if(this.rand < 0.05){
      iris.with.na[i,j] <- NA
    }
  }
}

write.table(iris.with.na,
            paste0(output.dir,"file5.csv"),
            quote = TRUE,
            sep=",",
            na="NULL",
            row.names=F,
            col.names=T)

write.table(iris.with.na,
            paste0(output.dir,"file6.csv"),
            quote = TRUE,
            sep=",",
            na="\\N",
            row.names=F,
            col.names=F)

write.table(iris.with.na,
            paste0(output.dir,"file7.csv"),
            quote = TRUE,
            sep=";",
            na="\\N",
            row.names=F,
            col.names=T)

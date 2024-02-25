library(less)
library(Rtsne)
library(ggplot2)
library('corrr')
library(ggcorrplot)
library("FactoMineR")
library("factoextra")

set.seed(10002)

setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

#metadata2 <- read.csv('./filtered_metadados_dataset.csv',header=TRUE)
meta_t <- read.csv('./metadata_woth_tracks.csv')

colnames(meta_t)

#Removing non-numeric attributes 
remove_row <- c(2,3,4,18)
filt_metadata <- meta_t[,-remove_row]
cor(filt_metadata)

#Removing fields 
remove_row2 <- c(7,10,13)
filt_metadata <- filt_metadata[,-remove_row2]

#Trying to understanding using graphs

#plot(valence ~ danceability, data=filt_metadata,col = c(1:10)[key])
#plot(acousticness ~ loudness, data=filt_metadata, col = c(1:10)[key])
#
#
#plot(energy ~ loudness, data=filt_metadata)
#
#
#plot(energy ~ loudness, data=filt_metadata, col = c(1:5)[time_signature])
#plot(energy ~ loudness, data=filt_metadata, col = c(1:10)[key])
#
#plot(energy ~ instrumentalness, data=filt_metadata, col = c(1:10)[key])
#plot(energy ~ acousticness, data=filt_metadata, col = c(1:10)[key])
#

## Implementing TSNE

# Install all the required packages
#install.packages("Rtsne")
#install.packages("ggplot2")#

# Load the required packages

tsne_out <- Rtsne(filt_metadata,check_duplicates = FALSE)

# Conversion of matrix to dataframe
tsne_plot <- data.frame(x = tsne_out$Y[,1], 
                        y = tsne_out$Y[,2])


# Plotting the plot using ggplot() function
ggplot2::ggplot(tsne_plot,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$danceability))

#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$energy))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$loudness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$acousticness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$instrumentalness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y, color = filt_metadata$loudness))
#

## Implementing KD Tree
musics <- c(52,53,102,164,178,202,213,269)

tree_t <- filt_metadata[-musics,]
test_t <- filt_metadata[musics,]
kdt <- KDTree$new(tree_t)

d <- kdt$query(query_X = test_t, k = 2)

rec_musics <- c()
for(i in 1:nrow(d$nn.idx)){
  rec_musics<- c(rec_musics,d$nn.idx[i,1])
  rec_musics<- c(rec_musics,d$nn.idx[i,2])
}

meta_t[rec_musics,]

# Com Scale
a <- scale(filt_metadata)
tree_t <- a[-musics,]
test_t <- a[musics,]
kdt <- KDTree$new(tree_t)

d <- kdt$query(query_X = test_t, k = 2)

rec_musics <- c()
for(i in 1:nrow(d$nn.idx)){
  rec_musics<- c(rec_musics,d$nn.idx[i,1])
  rec_musics<- c(rec_musics,d$nn.idx[i,2])
}

meta_t[rec_musics,c(1,2,4)]

#f_tree_t <- a
#b <- scale(my_acc[values])
#f_test_t <- b
#kdt <- KDTree$new(f_tree_t)

#metadata2 <- metadata2[,-c(1:2)]
#metadata2[t$nn.idx[1,],values]

f_tree_t <- a[-c(1:10),]
f_test_t <- a[c(1:10),]
kdt <- KDTree$new(f_tree_t)

t <- kdt$query(query_X = f_test_t, k = 3)

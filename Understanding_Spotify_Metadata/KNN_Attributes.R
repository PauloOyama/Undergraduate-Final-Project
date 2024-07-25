library(less)
library(Rtsne)
library(ggplot2)
library('corrr')
library(ggcorrplot)
library("FactoMineR")
library("factoextra")

set.seed(10002)

setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

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
#cor(filt_metadata)
#plot(valence ~ danceability, data=filt_metadata,col='deeppink3')
#plot(acousticness ~ loudness, data=filt_metadata,col='darkseagreen3')


#plot(energy ~ loudness, data=filt_metadata, col='gold3')

## Implementing t-SNE
tsne_out <- Rtsne(filt_metadata[,c(1,7,5,2,6)],check_duplicates = FALSE)

# Conversion of matrix to dataframe
tsne_plot <- data.frame(x = tsne_out$Y[,1], 
                        y = tsne_out$Y[,2])


# Plotting the plot using ggplot() function
ggplot2::ggplot(tsne_plot,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$danceability))


colnames(filt_metadata)
column_used <- c(1,7,2,6,5)
scaled_data <- scale(filt_metadata)
scaled_data <- scaled_data[,column_used]
## Implementing KD Tree
musics <- c(52,53,102,164,178,202,213,269)

tree_t <- scaled_data[-musics,]
test_t <- scaled_data[musics,]
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

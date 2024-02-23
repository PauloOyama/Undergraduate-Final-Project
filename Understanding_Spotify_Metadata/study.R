setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

metadata <- read.csv('./metadados_dataset.csv',header=TRUE)
metadata2 <- read.csv('./filtered_metadados_dataset.csv',header=TRUE)
my_acc <- read.csv('./my_account_12_02_2024_at_22h_45m.csv',header=TRUE)

colnames(metadata2)

my_acc <- my_acc[-c(12,13)]

filt_metadata <- metadata2[,-c(1,2,14,15)]
cor(filt_metadata)


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
library(Rtsne)
library(ggplot2)

tsne_out <- Rtsne(filt_metadata,check_duplicates = FALSE)


tsne_int <-Rtsne(filt_metadata[,values],check_duplicates = FALSE)

# Conversion of matrix to dataframe
tsne_plot <- data.frame(x = tsne_out$Y[,1], 
                        y = tsne_out$Y[,2])

tsne_plot2 <- data.frame(x = tsne_int$Y[,1], 
                        y = tsne_int$Y[,2])

# Plotting the plot using ggplot() function
#ggplot2::ggplot(tsne_plot,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$danceability))

#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$energy))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$loudness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$acousticness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$instrumentalness))
#ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y, color = filt_metadata$loudness))
#

## Implementing KD Tree

install.packages("less")

library(less)

data("iris")


tree_t <- filt_metadata[-c(1:2),]
test_t <- filt_metadata[c(1:2),]
kdt <- KDTree$new(tree_t)

kdt$query(query_X = test_t, k = 2)


#spotify:track:3dYD57lRAUcMHufyqn9GcI - Take me to Church
#spotify:track:35PKfoynRpVFoAUE3D5Kc6 - Work Song


#3296 - spotify:track:0LweQRsfJ3pRAJJFy6DrR1 - What Type Jessi
#22777 - spotify:track:5uPeD7XV8ADYo9pVpTQYmA - José Augusto
#23863 - spotify:track:7GBbqsq1ZCd1SPC5p47Wy5 - Flowmawell
#19373 - spotify:track:1EW7pgx7XA8OJMgys5usLJ - Drive ( The lightining Thief) 


values <- c(4,2,7,8,6,10)

values <- c(2,4,7,8)
a <- filt_metadata[,values]
a <- scale(a)

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

recommendation <- c()
for(i in c(1:nrow(t$nn.idx))){
  for(j in c(1:3)){
    recommendation <- append(recommendation,t$nn.idx[i,j])
  }
}

metadata2 <- metadata2[-c(1,2)]
df = metadata2[recommendation,] 

write.csv(df,file='A:/Universidade/TCC_Front/rec.csv')

# Music 1 - Take to Church
#spotify:track:13KczmU79sZ59yrpgvF9PC
#spotify:track:60cYr5uuMoxvyuIx45rGEW

#Music 2 - In the Cross of Christ
#spotify:track:3wNKnP17U6Yzv1N8jNtzPB 
#spotify:track:4PjMr4BC5vSKIsBji4WCNk

# Music 3 - Yo Soy Ivan
#spotify:track:4fCR5COPBAKXUJAhuUl5W7 
#spotify:track:6I9VzXrHxO9rA9A5euc8Ak

#[,1]  [,2]  [,3]
#[1,] 38274 28853 36248
#[2,]  1734  3674 30989
#[3,]  9299 38626 37881

#httr
#spotifyr

## Implement PCA=

library('corrr')
library(ggcorrplot)
library("FactoMineR")
library("factoextra")

str(filt_metadata)

colSums(is.na(filt_metadata))

data_normalized <- scale(filt_metadata)
head(data_normalized)
corr_matrix <- cor(data_normalized)

data.pca <- princomp(corr_matrix, cor=TRUE)
summary(data.pca)

fviz_eig(data.pca, addlabels = TRUE)

fviz_pca_var(data.pca, col.var = "black")

fviz_cos2(data.pca, choice = "var", axes = 1:2)# 

fviz_pca_var(data.pca, col.var = "cos2",
             gradient.cols = c("black", "orange", "green"),
             repel = TRUE)


is1 <- list()
is1$Comp.1 <- filt_metadata[1,] %*% data.pca$loadings[,1]
is1$Comp.2 <- filt_metadata %*% data.pca$loadings[,2]
is1$Comp.3 <- filt_metadata %*% data.pca$loadings[,3]
is1$Comp.4 <- filt_metadata %*% data.pca$loadings[,4]
is1$Comp.4 <- filt_metadata %*% data.pca$loadings[,5]
score1 <- as.data.frame(is1)

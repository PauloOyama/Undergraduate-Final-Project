setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

metadata <- read.csv('./metadados_dataset.csv',header=TRUE)
metadata2 <- read.csv('./filtered_metadados_dataset.csv',header=TRUE)


colnames(metadata2)

filt_metadata <- metadata2[,-c(1,2,14,15)]
cor(filt_metadata)
metadata$mode

hist(filt_metadata$valence, col=ra)

metadata$loudness
metadata$acousticness


plot(valence ~ danceability, data=filt_metadata,col = c(1:10)[key])
plot(acousticness ~ loudness, data=filt_metadata, col = c(1:10)[key])


plot(energy ~ loudness, data=filt_metadata)


plot(energy ~ loudness, data=filt_metadata, col = c(1:5)[time_signature])
plot(energy ~ loudness, data=filt_metadata, col = c(1:10)[key])

plot(energy ~ instrumentalness, data=filt_metadata, col = c(1:10)[key])
plot(energy ~ acousticness, data=filt_metadata, col = c(1:10)[key])


# Install all the required packages
install.packages("Rtsne")
install.packages("ggplot2")

# Load the required packages
library(Rtsne)
library(ggplot2)

data(iris)

# Remove Duplicate data present in iris
# data set(Otherwise Error will be generated)
remove_iris_dup <- unique(iris)

# Forming the matrix for the first four columns 
# of iris dataset because fifth column is of string type(Species)
iris_matrix <- as.matrix(remove_iris_dup[,1:4])

tsne_out <- Rtsne(filt_metadata,check_duplicates = FALSE)


tsne_int <-Rtsne(filt_metadata[,values],check_duplicates = FALSE)

# Conversion of matrix to dataframe
tsne_plot <- data.frame(x = tsne_out$Y[,1], 
                        y = tsne_out$Y[,2])

tsne_plot2 <- data.frame(x = tsne_int$Y[,1], 
                        y = tsne_int$Y[,2])

# Plotting the plot using ggplot() function
ggplot2::ggplot(tsne_plot,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$danceability))

ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$energy))
ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$loudness))
ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$acousticness))
ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$instrumentalness))
ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y,color=filt_metadata$tempo))


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

#valence
#tempo
#instrumentalness
#acousticness
#speechiness
#loudness
#energy
#danceability

#values <- c(1,2,4,6,7,8,10,11)
#values <- c(1,2,10)
values <- c(1,2,4,10)

#energy
#loudness
#acousticness      
#instrumentalness  
values <- c(2,4,7,8)
a <- filt_metadata[,values]

f_tree_t <- a[-c(1:2),]
f_test_t <- a[c(1:2),]
kdt <- KDTree$new(f_tree_t)

kdt$query(query_X = f_test_t, k = 2)

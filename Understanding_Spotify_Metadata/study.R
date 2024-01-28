setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

metadata <- read.csv('./metadados_dataset.csv',header=TRUE)


colnames(metadata)

filt_metadata <- metadata[,-c(1,13,14)]
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


tsne_int <-Rtsne(filt_metadata[,-c(3)],check_duplicates = FALSE)

# Conversion of matrix to dataframe
tsne_plot <- data.frame(x = tsne_out$Y[,1], 
                        y = tsne_out$Y[,2])

tsne_plot2 <- data.frame(x = tsne_int$Y[,1], 
                        y = tsne_int$Y[,2])

# Plotting the plot using ggplot() function
ggplot2::ggplot(tsne_plot,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$danceability))

ggplot2::ggplot(tsne_plot2,label=Species) + geom_point(aes(x=x,y=y, color=filt_metadata$key))




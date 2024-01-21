setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")

metadata <- read.csv('./metadados_dataset.csv',header=TRUE)


colnames(metadata)

filt_metadata <- metadata[,-c(1,12,13)]
cor(metadata)
metadata$mode

metadata$loudness
metadata$acousticness


plot(valence ~ danceability, data=filt_metadata, col = c(1:10)[key])
plot(acousticness ~ loudness, data=filt_metadata, col = c(1:10)[key])
plot(acousticness ~ loudness, data=filt_metadata, col = c(1:2)[mode])

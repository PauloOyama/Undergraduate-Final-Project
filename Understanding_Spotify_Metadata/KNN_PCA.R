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


## Implement PCA=


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


df<- data.frame(row.names = c('Comp.1','Comp.2','Comp.3','Comp.4','Comp.5','Comp.6','Comp.7','Comp.8','Comp.9','Comp.10','Comp.11'))

for(i in 1:nrow(data_normalized)){
    is1 <- list()
    is1$Comp.1 <- data_normalized[i,] %*% data.pca$loadings[,1]
    is1$Comp.2 <- data_normalized[i,] %*% data.pca$loadings[,2]
    is1$Comp.3 <- data_normalized[i,] %*% data.pca$loadings[,3]
    is1$Comp.4 <- data_normalized[i,] %*% data.pca$loadings[,4]
    is1$Comp.5 <- data_normalized[i,] %*% data.pca$loadings[,5]
    is1$Comp.6 <- data_normalized[i,] %*% data.pca$loadings[,6]
    is1$Comp.7 <- data_normalized[i,] %*% data.pca$loadings[,7]
    is1$Comp.8 <- data_normalized[i,] %*% data.pca$loadings[,8]
    is1$Comp.9 <- data_normalized[i,] %*% data.pca$loadings[,9]
    is1$Comp.10 <- data_normalized[i,] %*% data.pca$loadings[,10]
    is1$Comp.11 <- data_normalized[i,] %*% data.pca$loadings[,11]
    score1 <- as.data.frame(is1)
    df = rbind(df,score1)
}

df


musics <- c(52,53,102,164,178,202,213,269)

tree_t <- df[-musics,]
test_t <- df[musics,]
kdt <- KDTree$new(tree_t)

d <- kdt$query(query_X = test_t, k = 2)

rec_musics <- c()
for(i in 1:nrow(d$nn.idx)){
  rec_musics<- c(rec_musics,d$nn.idx[i,1])
  rec_musics<- c(rec_musics,d$nn.idx[i,2])
}

b <- meta_t[rec_musics,c(1,2,4)]



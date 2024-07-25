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



## Implement PCA
str(filt_metadata)

#colSums(is.na(filt_metadata))

data_normalized <- scale(filt_metadata)
head(data_normalized)

corr_matrix <- cor(data_normalized)

data.pca <- princomp(corr_matrix, cor=TRUE)

#PCA Visualization Part

#summary(data.pca)

#fviz_eig(data.pca, addlabels = TRUE)

#fviz_pca_var(data.pca, col.var = "black")

#fviz_cos2(data.pca, choice = "var", axes = 1:2) 

#fviz_pca_var(data.pca, col.var = "cos2",
            # gradient.cols = c("black", "orange", "green"),
             #repel = TRUE)


#Linear Combination between PCA result and the original dataframe
df<- data.frame(row.names = c('Comp.1','Comp.2','Comp.3','Comp.4','Comp.5','Comp.6','Comp.7','Comp.8','Comp.9','Comp.10','Comp.11'))
data_normalized <- data_normalized[,order(colnames(data_normalized))]
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

#Reading my account infos
my_account <- read.csv("./my_account.csv")

#Remove my account columns unused
remove_row3 <- c(4,6,13,14,16)
test_data <- my_account[,-remove_row3]

test_data <- test_data[,order(colnames(test_data))]
test_data <- scale(test_data)
df_test <- data.frame(row.names = c('Comp.1','Comp.2','Comp.3','Comp.4','Comp.5','Comp.6','Comp.7','Comp.8','Comp.9','Comp.10','Comp.11'))
for(i in 1:nrow(test_data)){
  is1 <- list()
  is1$Comp.1 <- test_data[i,] %*% data.pca$loadings[,1]
  is1$Comp.2 <- test_data[i,] %*% data.pca$loadings[,2]
  is1$Comp.3 <- test_data[i,] %*% data.pca$loadings[,3]
  is1$Comp.4 <- test_data[i,] %*% data.pca$loadings[,4]
  is1$Comp.5 <- test_data[i,] %*% data.pca$loadings[,5]
  is1$Comp.6 <- test_data[i,] %*% data.pca$loadings[,6]
  is1$Comp.7 <- test_data[i,] %*% data.pca$loadings[,7]
  is1$Comp.8 <- test_data[i,] %*% data.pca$loadings[,8]
  is1$Comp.9 <- test_data[i,] %*% data.pca$loadings[,9]
  is1$Comp.10 <- test_data[i,] %*% data.pca$loadings[,10]
  is1$Comp.11 <- test_data[i,] %*% data.pca$loadings[,11]
  score1 <- as.data.frame(is1)
  df_test = rbind(df_test,score1)
}

#Ktree with the first 5 dimensions
#[df] is the variable that has the 40000 musics 
#and [df_test] has the variable from my profile account
tree_t <- df[,c(1:5)]
test_t <- df_test[,c(1:5)]

kdt <- KDTree$new(tree_t)

d <- kdt$query(query_X = test_t, k = 2)

#Taking music recommendation index
rec_musics <- c()
for(i in 1:nrow(d$nn.idx)){
  rec_musics<- c(rec_musics,d$nn.idx[i,1])
  rec_musics<- c(rec_musics,d$nn.idx[i,2])
}

b <- meta_t[rec_musics,c(1,2,4)]


write.csv(b, "../Front/rec.csv", row.names=TRUE)

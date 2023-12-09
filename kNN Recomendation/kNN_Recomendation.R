setwd("A:/Universidade/TCC/Implementação/kNN Recomendation")

library(caret)

#Load csv from example
df <- read.csv("data/example_data.csv")


#Distance matrix from each point 
distance.matrix <- function(df)
{
  #Starting a matrix of n^2 data values
  distance <- matrix(rep(NA, nrow(df) ^ 2), nrow = nrow(df))

  for (i in 1:nrow(df))
  {
    for (j in 1:nrow(df))
    {
      #We're using Euclidean Distance
      distance[i, j] <- sqrt((df[i, 'X'] - df[j, 'X']) ^ 2 + (df[i, 'Y'] - df[j, 'Y']) ^ 2)
    }
  }
  return(distance)
}


#Just printing the matrix to make sure!
distance.matrix(df)


#Take the index from the k-neighbors from the point
k.nearest.neighbors <- function(i, distance, k = 5)
{
  return(order(distance[i, ])[2:(k + 1)])
}

#The knn algorithm implemented
knn <- function(df, k = 5)
{
  distance <- distance.matrix(df)
  predictions <- rep(NA, nrow(df))
  for (i in 1:nrow(df))
  {
    indices <- k.nearest.neighbors(i, distance, k = k)
    
    #In this case, we use the mean of the k-neighbors to predict if the 
    #given point is 0(spam) or 1(not spam)
    predictions[i] <- ifelse(mean(df[indices, 'Label']) > 0.5, 1, 0)
  }
  return(predictions)
}

knn(df)

df$kNNPredictions <- knn(df)

sum(with(df,Label != kNNPredictions))
confusionMatrix(data=as.factor(df$Label), reference = as.factor(df$kNNPredictions))

#Testing kNN from classes library
rm(knn)
library('class')

n <- nrow(df)
set.seed(1)
indices <- sort(sample(1:n, n * (1 / 2)))


training.x <- df[indices, 1:2]
test.x <- df[-indices, 1:2]
training.y <- df[indices, 3]
test.y <- df[-indices, 3]


predicted.y <- knn(training.x, test.x, training.y, k = 5)
sum(predicted.y != test.y)

length(test.y)


#Testing the effiency from glm instead of kNN
logit.model <- glm(Label ~ X + Y, data = df[indices, ])

predictions <- as.numeric(predict(logit.model, newdata = df[-indices, ]) > 0)

sum(predictions != test.y)
confusionMatrix(data=as.factor(test.y), reference = as.factor(predictions))

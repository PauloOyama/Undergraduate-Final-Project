#Build a df with 50 random points between 0 and 50
x <- runif(50, 0, 10)
y <- runif(50, 0, 10)
plot(x,y)
df <- data.frame(x,y)
df

#Distance Matrix 
distance.matrix <- function(df)
{
    #Making a matrix of n^2 data values
    distance <- matrix(rep(NA, nrow(df) ^ 2), nrow = nrow(df))

  for (i in 1:nrow(df))
  {
    for (j in 1:nrow(df))
    {
      distance[i, j] <- sqrt((df[i, 'x'] - df[j, 'x']) ^ 2 + (df[i, 'y'] - df[j, 'y']) ^ 2)
    }
  }
  return(distance)
}

#just printing df to make sure!
distance.matrix(df)


k.nearest.neighbors <- function(i, distance, k = 5)
{
  return(order(distance[i, ])[2:(k + 1)])
}


knn <- function(df, k = 5)
{
  distance <- distance.matrix(df)
  predictions <- rep(NA, nrow(df))
  for (i in 1:nrow(df))
  {
    indices <- k.nearest.neighbors(i, distance, k = k)
    predictions[i] <- ifelse(mean(df[indices, 'Label']) > 0.5, 1, 0)
  }
  return(predictions)
}

knn(df)

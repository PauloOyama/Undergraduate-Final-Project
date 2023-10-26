x <- runif(50, 0, 10)
y <- runif(50, 0, 10)
plot(x,y)
df <- data.frame(x,y)
df


distance.matrix <- function(df)
{
  #distance <- matrix(rep(NA, nrow(df) ^ 2), nrow = nrow(df))
  for (i in 1:nrow(df))
  {
    for (j in 1:nrow(df))
    {
      distance[i, j] <- sqrt((df[i, 'x'] - df[j, 'x']) ^ 2 + (df[i, 'y'] - df[j, 'y']) 
                             ^ 2)
    }
  }
  return(distance)
}

distance.matrix(df)

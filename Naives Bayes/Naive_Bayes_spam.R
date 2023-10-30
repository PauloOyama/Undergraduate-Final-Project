setwd("A:/Universidade/TCC/Implementação/Naives Bayes")

df = read.csv("data/spam_or_not_spam.csv")

set.seed(2)

sample <- sample(c(TRUE, FALSE), nrow(df), replace=TRUE, prob=c(0.7,0.3))
train  <- df[sample, ]
test   <- df[!sample, ]

spam = length(train$label[train$label != 0])
not_spam = length(train$label) - spam


#Time to code

df2 <- data.frame(words=c(""),spam=c(0),ham=c(0))
for (i in 1:nrow(train)){
  
  if(train[i,1] == ""){
    next
  }
  
  #find duplicated values
  words_dup = duplicated(strsplit(train[i,1],"[[:space:]]")[[1]])
  
  #take the distinct value
  words = strsplit(train[i,1],"[[:space:]]")[[1]][!words_dup]
  
  for (j in 1:length(words)){
    if(words[j] %in% df2$words){
      if(train[i,2] == 0){
        df2$ham[df2$words == words[j]] = df2$ham[df2$words == words[j]] + 1
      }else{
        df2$spam[df2$words == words[j]] = df2$spam[df2$words == words[j]] + 1
      }
    }else{
      df2[nrow(df2)+1,1] = c(words[j])
      if(train[i,2] == 0){
        df2[nrow(df2),2] = c(0)  
        df2[nrow(df2),3] = c(1)  
      }else{
        df2[nrow(df2),2] = c(1)  
        df2[nrow(df2),3] = c(1)  
      }
    }
  }
  
  #Maybe remove "" and NUMBER string ? 
}
rm(i)
for(i in 1:nrow(df2)){
  df2$spam[i] = df2$spam[i]/spam
  df2$ham[i] = df2$ham[i]/not_spam
}


for(i in 1:nrow(test)){
  
  #find duplicated values
  words_dup = duplicated(strsplit(test[i,1],"[[:space:]]")[[1]])
  
  #take the distinct value
  words = strsplit(test[i,1],"[[:space:]]")[[1]][!words_dup]
  
  #ham
  for (j in 1:nrow(df2)){
    for (j in 1:length(words)){
      probability = 1
      if(words[j] %in% df2$words){
        
      }
    }
  }
}

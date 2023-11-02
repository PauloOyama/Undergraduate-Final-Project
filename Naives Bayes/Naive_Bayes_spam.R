#All credits to
#https://bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

setwd("A:/Universidade/TCC/Implementação/Naives Bayes")

library(caret)

df = read.csv("data/spam_or_not_spam.csv")
stopwords = read.table(file="data/stopwords.txt", header=TRUE)
stopwords[nrow(stopwords)+1,] = 'a'


#FUNCTIONS

tokenize <- function(msg){
  
  #find duplicated values in a string
  words_dup = duplicated(strsplit(msg,"[[:space:]]")[[1]])
  
  #remove the duplicated values(TOKENS)
  tokens = strsplit(msg,"[[:space:]]")[[1]][!words_dup]
  
  return (tokens)
}

set.seed(1)

#Dividing in train an test (70,30)
sample <- sample(c(TRUE, FALSE), nrow(df), replace=TRUE, prob=c(0.7,0.3))
train  <- df[sample, ]
test   <- df[!sample, ]

#Take the number of spam and non spam
spam = length(train$label[train$label != 0])
not_spam = length(train$label) - spam

#Take the probability of be spam and non spam regarding the total number
p_spam = spam/length(train$label)
p_not_spam = not_spam/length(train$label)

#Time to code
df2 <- data.frame(words=c(""),spam=c(0),ham=c(0))
for (i in 1:nrow(train)){
  
  #Messages without any word
  if(train[i,1] == ""){
    next
  }

  words = tokenize(train[i,1])
  
  for (j in 1:length(words)){
    if(words[j] %in% stopwords$a){
      next
    }
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


for(i in 1:nrow(df2)){
  df2$p_spam[i] = df2$spam[i]/spam
  df2$p_ham[i] = df2$ham[i]/not_spam
}


for(i in 1:nrow(test)){
  
  #find duplicated values
  words_dup = duplicated(strsplit(test[i,1],"[[:space:]]")[[1]])
  
  #take the distinct value
  words = strsplit(test[i,1],"[[:space:]]")[[1]][!words_dup]
  
#spam
probability_spam = 0
for (j in 1:length(words)){
  wd = df2$p_spam[df2$words == words[j]]
  if(words[j] %in% df2$words && wd != 0){
    probability_spam = probability_spam + log(df2$p_spam[df2$words == words[j]])
  }else{
    next
  }
}


#ham
probability_ham = 0
for (j in 1:length(words)){
  wd = df2$p_ham[df2$words == words[j]]
  if(words[j] %in% df2$words && wd != 0){
    probability_ham = probability_ham + log(df2$p_ham[df2$words == words[j]])
  }else{
    next
  }
}
upper <- probability_spam+log(p_spam)
lower <- probability_spam+log(p_spam) + probability_ham+log(p_not_spam) 
test$prob[i] <-  ifelse(upper/lower > 0.5, 1, 0)
test$q <- upper/lower

}

example <- confusionMatrix(data=as.factor(test$prob), reference = as.factor(test$label))
example


#All credits to
#https://bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

setwd("A:/Universidade/TCC/Implementação/Naives Bayes")

library(caret)

df = read.csv("data/spam_or_not_spam.csv")
stopwords = read.table(file="data/stopwords.txt", header=TRUE)
stopwords[nrow(stopwords)+1,] = 'a'

############################################################################
#FUNCTIONS
############################################################################

tokenize <- function(msg){
  
  #find duplicated values in a string
  words_dup = duplicated(strsplit(tolower(msg),"[[:space:]]")[[1]])
  
  #remove the duplicated values(TOKENS)
  tokens = strsplit(msg,"[[:space:]]")[[1]][!words_dup]
  
  tokens = tokens[nchar(tokens)>3]
  
  return (tokens)
}

token_frequency <- function(train){
  table_frequency <- data.frame(words=c(""),spam=c(0),ham=c(0))
  for (i in 1:nrow(train)){
    
    #Messages without any word
    if(train[i,1] == ""){
      next
    }
    
    words = tokenize(train[i,1])
    
    if(length(words) == 0){
      next
    }
    
    for (j in 1:length(words)){
      if(words[j] %in% stopwords$a){
        next
      }
      if(words[j] %in% table_frequency$words){
        if(train[i,2] == 0){
          table_frequency$ham[table_frequency$words == words[j]] = table_frequency$ham[table_frequency$words == words[j]] + 1
        }else{
          table_frequency$spam[table_frequency$words == words[j]] = table_frequency$spam[table_frequency$words == words[j]] + 1
        }
      }else{
        table_frequency[nrow(table_frequency)+1,1] = c(words[j])
        if(train[i,2] == 0){
          table_frequency[nrow(table_frequency),2] = c(0)  
          table_frequency[nrow(table_frequency),3] = c(1)  
        }else{
          table_frequency[nrow(table_frequency),2] = c(1)  
          table_frequency[nrow(table_frequency),3] = c(1)  
        }
      }
    }
    
    #Maybe remove "" and NUMBER string ? 
  }
  return (table_frequency)
}

############################################################################
#MAIN
############################################################################

set.seed(sample(1:100,1))


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


#Creating a table with the frequency of each token given spam or not spam
table_frequency <- token_frequency(train)


#creating a column for the probability of each word given spam or not spam
for(i in 1:nrow(table_frequency)){
  table_frequency$p_spam[i] = table_frequency$spam[i]/spam
  table_frequency$p_ham[i] = table_frequency$ham[i]/not_spam
}

#Testing the created model
for(i in 1:nrow(test)){
  
  words <- tokenize(test[i,1])
  print(i)
  if(length(words) == 0){
    next
  }
  
  #probability of all the words be spam
  probability_spam = 0
  for (j in 1:length(words)){
    p_word = table_frequency$p_spam[table_frequency$words == words[j]]
    if(words[j] %in% table_frequency$words && p_word != 0){
      probability_spam = probability_spam + log(p_word)
    }else{
      next
    }
  }


  #probability of all the words not be spam
  probability_ham = 0
  for (j in 1:length(words)){
    p_word = table_frequency$p_ham[table_frequency$words == words[j]]
    if(words[j] %in% table_frequency$words && p_word != 0){
      probability_ham = probability_ham + log(p_word)
    }else{
      next
    }
  }
  
  
  upper <- probability_spam+log(p_spam)
  lower <- probability_spam+log(p_spam) + probability_ham+log(p_not_spam) 
  test$predict[i] <-  ifelse(upper/lower > 0.5, 1, 0)
  test$probability[i] <- upper/lower
}

example <- confusionMatrix(data=as.factor(test$predict), reference = as.factor(test$label))
example


#nesta primeira parte, vou fazer o tratamento dos dados, tirar um "lixinho" que vem dentro da variavel de genero musical, por exemplo.

library(stringr)
library(ggplot2)
library(factoextra)
library(rpart)
library(rpart.plot)

setwd("A:/Universidade/TCC/Implementação/Understanding_Spotify_Metadata/")
dados <- read.csv("DataSet_With_Genre.csv")
str(dados)

str_view_all(dados$genres[991], '(\\{(")?)| (\\") |((\\")?\\})')

generos <- str_replace_all(dados$genres, '(\\{(")?)|((\\")?\\})', "")

generos <- str_replace_all(generos, '\\"', "")

generos <- str_extract(generos, "[^,]+")
unique(generos)


#vamos trabalhar apenas com os generos mais populares, no caso a seguir escolheu-se os dez generos mais populares
generos_populares <- names(sort(table(generos), decreasing = TRUE)[1:10])

indices_generos_populares <- generos %in% generos_populares

dados_populares <- dados[indices_generos_populares,]
dados_populares$genres

dados_populares$genres <- generos[indices_generos_populares]
dados_populares$genres <- as.factor(dados_populares$genres)


dados_populares_escalonado <- scale(dados_populares[,-c(1,2,4,5,6,18,20)])

plot(prcomp(dados_populares_escalonado)) #variaveis mais importantes para o PCA

spotify_km <- kmeans(x = dados_populares_escalonado,
                     centers = 3, nstart = 10)


fviz_cluster(object = spotify_km,
             data = dados_populares_escalonado, labelsize = 1)

#parece que com 3 clusters apenas não é um bom processo de separacao; aumentar o numero de cluster e verificar o que acontece ou trabalhar com menos generos.

dados_populares$cluster <- as.factor(spotify_km$cluster)

table(dados_populares$genres[spotify_km$cluster == 1]) #instrumental, bossa nova

table(dados_populares$genres[spotify_km$cluster == 2]) #brazilian hip hop

table(dados_populares$genres[spotify_km$cluster == 3])


ggplot(dados_populares, aes(x = genres, y = danceability))+
  geom_boxplot() #classical

ggplot(dados_populares, aes(x = genres, y = energy))+
  geom_boxplot()


#identificar as posicoes de cada genero e trabalhar com apenas 3: classico, hip hop, metal

is.rock <- str_detect(dados_populares$genres, "rock")

is.bossa <- str_detect(dados_populares$genres, "bossa")

is.metal <- str_detect(dados_populares$genres, "metal")

is.gospel <- str_detect(dados_populares$genres, "gospel")

is.pop <- str_detect(dados_populares$genres, "pop")

is.hiphop <- str_detect(dados_populares$genres, "hip")

is.classical <- str_detect(dados_populares$genres, "classical")

dados_populares2 <- dados_populares

dados_populares2$categoria <- NA

dados_populares2$categoria[is.bossa] <- "bossa"
dados_populares2$categoria[is.rock] <- "rock"
dados_populares2$categoria[is.gospel] <- "gospel"
dados_populares2$categoria[is.metal] <- "metal"
dados_populares2$categoria[is.pop] <- "pop"
dados_populares2$categoria[is.classical] <- "classical"
dados_populares2$categoria[is.hiphop] <- "hip hop"

dados_populares2 <- dados_populares2[,-c(1,2,3,4,5,6,9,12,15,18,20,21)]

#arvore de decisao para prever o genero a partir das informacoes de cada musica

N <- round(0.8*nrow(dados_populares2))
treino <- dados_populares2[1:N,]
teste <- dados_populares2[-(1:N),]

arvore <- rpart(categoria ~., treino, method = "class")

rpart.plot(arvore)
previsao <- predict(arvore, teste, type = "class")
mean(previsao == teste$categoria) #baixa acuracia

#vamos melhorar a acuracia trabalhando com 3 generos apenas

dados_populares3 <- dados_populares2[dados_populares2$categoria %in% c("metal", "hip hop", "classical"),] 

str(dados_populares3)
dados_populares3$categoria <- as.factor(dados_populares3$categoria)

N <- round(0.8*nrow(dados_populares3))
treino <- dados_populares3[1:N,]
teste <- dados_populares3[-(1:N),]

arvore <- rpart(categoria ~., treino, method = "class")

rpart.plot(arvore, extra = 101)
previsao <- predict(arvore, teste, type = "class")
mean(previsao == teste$categoria)

#############################################
#clusterização
#############################################
str(dados_populares3)
dados_scaled <- scale(dados_populares3[,-10])
plot(prcomp(dados_scaled))

spotify_km <- kmeans(x = dados_scaled,
                     centers = 3, nstart = 10)

spotify_km$size

fviz_cluster(object = spotify_km,
             data = dados_populares3[,-10], labelsize = 1)

table(dados_populares3$categoria[spotify_km$cluster == 1])
table(dados_populares3$categoria[spotify_km$cluster == 2])
table(dados_populares3$categoria[spotify_km$cluster == 3])
#bem dividido!
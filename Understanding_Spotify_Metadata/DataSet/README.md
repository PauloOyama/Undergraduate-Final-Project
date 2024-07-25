# Understanding the DataSet 

## More Infos

This datasets come from de Spotify's API so for more information, click in the link below,

 [API Documentation](https://developer.spotify.com/documentation/web-api)

## About

The DataSets were constructed with scrapping in the APIs using Python and later analysed with R,
they consist in a few .csv files each one has its purpose.

But for now, let's talk about it's columns.

| Nome            | Tipo        | Descrição                    |
|-----------------|-------------|------------------------------|
| Name            | chr         | string                       |
| Track Id         | chr         | string                       |
| URI             | chr         | string                       |
| Mode            | int         | range[0,1]                   |
| Key             | int         | range[-1,...,11]             |
| Time signature   | int         | range[3,...,7]               |
| Popularity      | int         | range[0...100]               |
| Acousticness    | float       | range[0, ... ,1.0]           |
| Danceability    | float       | range[0...1.0]               |
| Energy          | float       | range[0...1.0]               |
| Instrumentalness| float       | range[0...1.0]               |
| Loudness        | float       | range[-60.0...0]             |
| Liveness        | float       | range[0...1.0]               |
| Speechiness     | float       | range[0...1.0]               |
| Valence         | float       | range[0...1.0]               |
| Duration(ms)      | float       | range[0...Infinity]          |
| Tempo           | float       | range[0...Infinity]          |
| Created at       | datetime    | %YY-%MM-%DDhh:mm:ss          |

The file *DataSet_With_Genre.csv* contains also the genres from the musics;
The file *metadata_woth_tracks.csv* contains the popularity and the metadata of the music;
The files *metadados_dataset.csv* and *filtered_metadados_dataset.csv* contains almost the same columns.;
The file *my_account.csv* contains just 20 musics that are the tracks most listen by me, 
i used this file as input to the machine learning model.
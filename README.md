# Recommendation App: recomendação de músicas do Spotify com kNN

Trabalho de conclusão de curso de **Paulo K. Oyama** na Universidade Federal de Uberlândia (UFU). O texto completo está em [`TCC-Paulo_K_Oyama_F.pdf`](TCC-Paulo_K_Oyama_F.pdf).

O app lê as 20 faixas mais ouvidas de uma conta do Spotify. Para cada uma, encontra as 2 mais parecidas numa base de cerca de 40 mil músicas, comparando os atributos de áudio com PCA e kNN. Depois cria na conta uma playlist privada chamada **TCC** com essas 40 recomendações.

## Estrutura do repositório

| Pasta | O que tem |
|---|---|
| [`Front/`](Front) | O app: servidor FastAPI (`main.py`), a página do app (`index.html`) e a página da expansão da base (`expansao.html`) |
| [`Scrapping_api/`](Scrapping_api) | A coleta de músicas: os scripts originais de 2023–2024 e o módulo novo de expansão (`expansion/`, `discover.py`, `expansion_server.py`) |
| [`Understanding_Spotify_Metadata/`](Understanding_Spotify_Metadata) | A análise em R (PCA, kNN, t-SNE, clusterização) e as bases em `DataSet/` |
| [`Tests/`](Tests) | Experimentos de estudo: kNN, Naive Bayes e um notebook sobre outra base de músicas |

## Como funciona

```
Spotify (sua conta)                    Base de músicas (DataSet/)
  └─ top 20 faixas ──┐                   └─ ~40 mil faixas com 11 atributos de áudio
                     ▼                                │
             atributos de áudio ──► PCA (5 componentes) ──► kNN (k = 2, árvore KD)
                                                      │
                                    Front/rec.csv (40 recomendações)
                                                      │
                                  playlist privada "TCC" na sua conta
```

Os 11 atributos comparados são popularidade, acousticness, danceability, duração, energy, instrumentalness, loudness, liveness, speechiness, tempo e valence. O cálculo fica em [`Understanding_Spotify_Metadata/KNN_PCA.R`](Understanding_Spotify_Metadata/KNN_PCA.R).

## Configuração

1. **Python 3.10 ou mais novo.** Na raiz do projeto:
   ```bash
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt     # Windows
   .venv/bin/python -m pip install -r requirements.txt         # Linux e macOS
   ```
2. **Um app no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).** Em **Settings → Redirect URIs**, cadastre exatamente `http://127.0.0.1:8000/callback`.
3. **Um arquivo `.env` na raiz**, que está no `.gitignore` e nunca vai para o git:
   ```env
   SPOTIPY_CLIENT_ID=...
   SPOTIPY_CLIENT_SECRET=...
   # opcional, para a expansão da base:
   LASTFM_API_KEY=...
   ```

## Rodar o app

```bash
cd Front
../.venv/Scripts/python -m uvicorn main:app --port 8000 --env-file ../.env
```

Abra **http://127.0.0.1:8000/**, use `127.0.0.1` e não `localhost`, e clique em **Criar minha playlist**:

1. Na primeira vez, o botão leva ao login do Spotify. O servidor guarda o acesso só na memória.
2. De volta à página, clique de novo. A playlist **TCC** é criada com as faixas de `Front/rec.csv`.

| Rota | O que faz |
|---|---|
| `GET /` | A página do app |
| `GET /login`, `GET /callback` | Login no Spotify (Authorization Code) |
| `GET /status` | Quem está conectado |
| `GET /items/{id}` | Salva o seu top 20 com atributos em `Understanding_Spotify_Metadata/my_account.csv` |
| `GET /playlist/{id}` | Cria a playlist TCC com as faixas de `rec.csv` |

**Outras pessoas:** em development mode, o Spotify só deixa entrar contas cadastradas em **Settings → User Management**, no máximo 5. O servidor guarda um login de cada vez.

## A base de músicas

### Como foi coletada (2023–2024)

Os scripts em `Scrapping_api/` usam Client Credentials e rodam em sequência. Cada arquivo processado recebe o prefixo `OK_`.

| Etapa | Script | Endpoint do Spotify | Resultado |
|---|---|---|---|
| Sementes | `artists/credential.py` | Search, com nomes digitados à mão | 415 artistas |
| Expansão | `artists/related_artists.py` | Related Artists | 4.688 artistas únicos |
| Faixas | `top_tracks_f/top_tracks.py` | Artist's Top Tracks (Brasil) | 62.528 faixas |
| Atributos | `track_features/metadados.py` | Audio Features | 69.028 linhas |
| CSV | `metadados_csv.py`, `filter_dataset.py` | — | 39.904 faixas sem duplicatas |

A base final, `DataSet/metadata_worth_tracks.csv`, tem 39.948 faixas. Como começou de artistas escolhidos à mão e só pegou as mais tocadas de cada um, ela é concentrada em rock, MPB, samba, rap e k-pop, e tem pouca cauda longa.

### O que mudou na API do Spotify

- **Desde novembro de 2024**, apps novos não acessam Audio Features, Related Artists, Recommendations nem as playlists editoriais. Este app recebe 403 em Audio Features e 404 em Related Artists.
- **Desde fevereiro de 2026**, apps novos em development mode também perderam Top Tracks, os endpoints em lote e o campo `popularity`, e a busca devolve no máximo 10 itens por página. Para apps antigos, como este, o Spotify adiou esse corte sem data.
- **Termos de uso:** a documentação proíbe usar conteúdo do Spotify para treinar modelos de machine learning.

Fontes: [mudanças de nov/2024](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api), [guia de fev/2026](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide), [quota modes](https://developer.spotify.com/documentation/web-api/concepts/quota-modes).

### Expansão da base (2026)

O módulo [`Scrapping_api/expansion/`](Scrapping_api/expansion) usa o Spotify só como catálogo e busca os atributos fora dele:

| Etapa | Comando | Fonte |
|---|---|---|
| Busca | `discover.py search --cells 20` | Spotify Search: uma grade de 717 consultas por gênero, década e país, com teto de faixas por consulta |
| Artistas | `discover.py artists --max 100` | Álbuns e singles de cada artista novo, até 5 faixas por artista |
| Enriquecimento | `discover.py enrich` | ISRC, popularidade e gêneros (Spotify); ouvintes (Last.fm, opcional) |
| Atributos | `discover.py features` | [ReccoBeats](https://reccobeats.com): os mesmos atributos do Spotify, pelo ID da faixa |
| Exportação | `discover.py export` | Remove duplicatas por URI e ISRC e grava `DataSet/expansion_tracks.csv` |
| Relatório | `discover.py report` | Diversidade antes × depois em `expansion_data/diversity.json` |

Rode os comandos dentro de `Scrapping_api/`. Cada etapa salva o progresso em `Scrapping_api/expansion_data/` e retoma de onde parou.

**Interface web:**

```bash
cd Scrapping_api
../.venv/Scripts/python -m uvicorn expansion_server:app --port 8010 --env-file ../.env
```

Abra **http://127.0.0.1:8010/**. A página roda as etapas e mostra o progresso ao vivo e o relatório de diversidade.

**Primeira rodada** (15 consultas, 1.884 faixas descobertas):

| | Base antiga | Depois da expansão |
|---|---|---|
| Faixas com gênero | 36.036 | 36.793 |
| Artistas | 4.176 | 4.483 |
| Gêneros | 710 | 769 |
| Faixas de cauda longa (popularidade < 30) | 36,1% | 36,8% |

O ReccoBeats tinha atributos para 61% das faixas descobertas. 72% das faixas novas são de cauda longa, e elas cobrem lançamentos de 1960 a 2020.

## Análise em R

Em `Understanding_Spotify_Metadata/`, rode a partir da própria pasta:

```bash
Rscript KNN_PCA.R
```

O script lê `DataSet/metadata_worth_tracks.csv`, mais `DataSet/expansion_tracks.csv` se existir, e o `my_account.csv` gerado pela rota `/items`. Ele grava as recomendações em `Front/rec.csv`. Os outros scripts (`KNN_Attributes.R`, `clusterizacao2_tcc.R`) são as análises exploratórias do TCC. A descrição das colunas das bases está em [`DataSet/README.md`](Understanding_Spotify_Metadata/DataSet/README.md).

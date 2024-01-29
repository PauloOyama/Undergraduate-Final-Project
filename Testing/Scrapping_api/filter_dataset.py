import pandas as pd

df = pd.read_csv("./json_csv/metadados_dataset.csv")

filtered = df.drop_duplicates(subset=["uri"])

filtered.to_csv("./json_csv/filtered_metadados_dataset.csv")

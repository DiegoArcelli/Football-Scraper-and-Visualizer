import pandas as pd
import argparse
import unidecode

def normalize(text):
    return unidecode.unidecode(text)

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--query', default="divock", type=str)

args = parser.parse_args()


season = args.season
query = args.query

data_path = f"./../../datasets/{season}/players.csv"

data = pd.read_csv(data_path)
data = data[["player_id", "player"]]

players = data["player"].apply(lambda x: normalize(x.lower()))
data["name"] = players

print(len(data))
data = data[data["name"].str.contains(query)]

print(data[["player_id", "player"]])


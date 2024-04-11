import numpy as np
import sqlite3
import os
import pandas as pd


def extract_table_name_from_path(file_path, n=4):
    elements = file_path.split("/")[-n:]
    elements[-1] = elements[-1].split(".")[0]
    elements = [element.replace("-", "_").replace("'", "").upper() for element in elements]
    return "_".join(elements[::-1])


def fix_minutes(minutes):
    return minutes.map(lambda x: int(x.replace(",", "")))


def create_table(df, table_name, conn, cursor):

    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()

    create_query = f"CREATE TABLE {table_name} ("

    type_map = {
        "object": "STRING",
        "int64": "INT",
        "int32": "INT",
        "float64": "FLOAT",
        "float32": "FLOAT",
    }

    for column in df.columns:
        if column == "minutes" and df[column].dtype == 'object':
            df[column] = fix_minutes(df[column])

        # types[column] = df[column].dtype
        
        dtype = str(df[column].dtype)

        create_query += f"{column} {type_map[dtype]}, "

    create_query = create_query[:-2]
    create_query += f")"

    cursor.execute(create_query)
    conn.commit()

    insert_query = f"INSERT INTO {table_name} ({','.join(df.columns)}) VALUES "

    for idx in df.index:
        insert_query += "("
        for column in df.columns:
            value = df[column][idx]
            
            if type(value) == str:
                value = f"\"{value}\""

            if pd.isna(value):
                value = "NULL"
            
            insert_query += f"{value},"

        insert_query = insert_query[:-1] + "), "

    insert_query = insert_query[:-2]
    # print(insert_query)

    cursor.execute(insert_query)
    conn.commit()

    
def check_season(s):
    
    splits = s.split("-")

    if len(splits) != 2:
        return False

    try:
        n1 = int(splits[0])
        n2 = int(splits[1])
    except ValueError:
        return False

    if n2 != n1 + 1:
        return False

    return True


def get_directories(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def get_files(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


root_dir = "./../../"
datasets_dir = f"{root_dir}datasets/"
conn = sqlite3.connect(f"{root_dir}databases/football.db")
cursor = conn.cursor()


season_directories = [f"{datasets_dir}{d}/" for d in get_directories(datasets_dir) if check_season(d)]

for season_dir in season_directories:
    leagues_directories = [f"{season_dir}{d}/" for d in get_directories(season_dir) if d != "All-Competitions"]
    season_files = [f"{season_dir}{f}" for f in get_files(season_dir) if f.endswith(".csv")]
    print(season_dir)

    for file in season_files:
        table_name = extract_table_name_from_path(file, 2)
        print("\t", file, table_name)
        df = pd.read_csv(file)
        create_table(df, table_name, conn, cursor)

    for league_dir in leagues_directories:
        teams_directories = [f"{league_dir}{d}/" for d in get_directories(league_dir)]
        teams_files = [f"{league_dir}{f}" for f in get_files(league_dir) if f.endswith(".csv")]
        print("\t", league_dir)
        
        for file in teams_files:
            table_name = extract_table_name_from_path(file, 3)
            print("\t\t", file, table_name)
            df = pd.read_csv(file)
            create_table(df, table_name, conn, cursor)

        for team_dir in teams_directories:
            print("\t\t", team_dir)
            team_files = [f"{team_dir}{f}" for f in get_files(team_dir) if f.endswith(".csv")]
            for file in team_files:
                table_name = extract_table_name_from_path(file, 4)
                print("\t\t\t", file, table_name)
                df = pd.read_csv(file)
                create_table(df, table_name, conn, cursor)
                
conn.close()

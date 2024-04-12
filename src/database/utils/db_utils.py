import numpy as np
import sqlite3
import os
import pandas as pd

SEP_STR = "  "

admissible_files = [
    "team.csv",
    "opponents.csv",
    "players.csv",
    "goalkeepers.csv"
]


def extract_last_element_form_path(path, n=1):
    if path.endswith("/"):
        return path.split("/")[-2] + "/"
    elif path.endswith(".csv"):
        return path.split("/")[-1]


def extract_element_form_path(path, n=1):
    return path.split("/")[-n] + "/"


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

            try:
                if pd.isna(value):
                    value = "NULL"
            except ValueError:
                print(value)
                exit()
            
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
    admissible_files = [f"{f}.csv" for f in ["team", "opponents", "players", "goalkeepers"]]
    all_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] 
    filtered_files = [f"{path}{f}" for f in all_files if f.endswith(".csv") and f in admissible_files]
    return filtered_files


def create_databases(
        database_dir : str = "./../../databases/",
        dataset_dir : str = "./../../datasets/",
        season : str = None,
        league : str = None,
        team : str = None
    ) -> None:
    

    database_dir = database_dir if database_dir[-1] == "/" else database_dir + "/"
    dataset_dir = dataset_dir if dataset_dir[-1] == "/" else dataset_dir + "/"

    conn = sqlite3.connect(f"{database_dir}football.db")
    cursor = conn.cursor()

    if season is None:
        season_directories = [f"{dataset_dir}{d}/" for d in get_directories(dataset_dir) if check_season(d)]
    else:
        season_directories = [f"{dataset_dir}{season}/"]


    print(dataset_dir)
    print("|")
    print("|")
    for season_dir in season_directories:
        print(f"|__{extract_last_element_form_path(season_dir)}")

        if league is None:
            leagues_directories = [f"{season_dir}{d}/" for d in get_directories(season_dir) if d != "All-Competitions"]
        else:
            leagues_directories = [f"{season_dir}{league}/"]
        season_files = get_files(season_dir) #[f"{season_dir}{f}" for f in get_files(season_dir) if f.endswith(".csv")]

        s = "|" if season_dir != season_directories[-1] else " "

        for file in season_files:
            table_name = extract_table_name_from_path(file, 2)
            print(f"{s}{SEP_STR*2}|__", extract_last_element_form_path(file), table_name)
            df = pd.read_csv(file)
            create_table(df, table_name, conn, cursor)
        print(f"{s}{SEP_STR*2}|")
        print(f"{s}{SEP_STR*2}|")

        for league_dir in leagues_directories:
            print(f"{s}{SEP_STR*2}|__{extract_last_element_form_path(league_dir)}")

            if team is None:
                teams_directories = [f"{league_dir}{d}/" for d in get_directories(league_dir)]
            else:
                teams_directories = [f"{league_dir}{team}/"]
                
            teams_files = get_files(league_dir)#[f"{league_dir}{f}" for f in get_files(league_dir) if f.endswith(".csv")]
            
            for file in teams_files:
                table_name = extract_table_name_from_path(file, 3)
                c = "|" if league_dir != leagues_directories[-1] else " " 
                print(f"{s}{SEP_STR*2}{c}{SEP_STR*2}|__{extract_last_element_form_path(file)}", table_name)
                df = pd.read_csv(file)
                create_table(df, table_name, conn, cursor)

            for team_dir in teams_directories:
                c = "|" if league_dir != leagues_directories[-1] else " "
                print(f"{s}{SEP_STR*2}{c}{SEP_STR*2}|")
                print(f"{s}{SEP_STR*2}{c}{SEP_STR*2}|")
                print(f"{s}{SEP_STR*2}{c}{SEP_STR*2}|__{extract_last_element_form_path(team_dir)}")
                team_files = get_files(team_dir)# [f"{team_dir}{f}" for f in get_files(team_dir) if f.endswith(".csv") and f in admissible_files]
                for file in team_files:
                    table_name = extract_table_name_from_path(file, 4)
                    c1 = " " if league_dir == leagues_directories[-1] else "|" 
                    c2 = " " if team_dir == teams_directories[-1] else "|"
                    print(f"{s}{SEP_STR*2}{c1}{SEP_STR*2}{c2}{SEP_STR*2}|__{extract_last_element_form_path(file)}", table_name)      
                    df = pd.read_csv(file)
                    create_table(df, table_name, conn, cursor)

            c = "|" if league_dir != leagues_directories[-1] else ""
            print(f"{s}{SEP_STR*2}{c}")
            print(f"{s}{SEP_STR*2}{c}")

                    
    conn.close()

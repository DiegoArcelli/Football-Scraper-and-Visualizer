import os
import pandas as pd

def get_league_id(league_name):
    if league_name == "Serie-A":
        return 11
    elif league_name == "Premier-League":
        return 9
    elif league_name == "La-Liga":
        return 12
    elif league_name == "Bundesliga":
        return 20
    elif league_name == "Ligue-1":
        return 13
    elif league_name == "Champions-League":
        return 8
  


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def merge_data_frames(df_list, ref_col):
    merged_df = df_list[0]
    for df in df_list[1:]:
        merged_df = pd.merge(merged_df, df, on=ref_col, how='inner', suffixes=('', '_to_drop'))
        merged_df = merged_df[[col for col in merged_df.columns if not col.endswith("_to_drop")]]
    return merged_df
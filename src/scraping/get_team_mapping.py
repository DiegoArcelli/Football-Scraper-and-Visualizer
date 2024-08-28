import argparse
from default_arguments import *
import json

def read_file(file_path):
    with open(file_path, "r") as f:
        text = f.read()
        lines = text.split("\n")
    return lines

def get_lcs_length(S1, S2):
    m = len(S1)
    n = len(S2)

    # Initializing a matrix of size (m+1)*(n+1)
    dp = [[0] * (n + 1) for x in range(m + 1)]

    # Building dp[m+1][n+1] in bottom-up fashion
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if S1[i - 1] == S2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j],
                               dp[i][j - 1])

    # dp[m][n] contains length of LCS for S1[0..m-1]
    # and S2[0..n-1]
    return dp[m][n]

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
args = parser.parse_args()


data_path = args.data_path
season = args.season
league = args.league

fbref_names_path = f"{data_path}{season}/{league}/fbref_names.txt"
whoscored_names_path = f"{data_path}{season}/{league}/whoscored_names.txt"

fbref_names = read_file(fbref_names_path)
whoscored_names = read_file(whoscored_names_path)

names_mapping = {}

for fbref_name in fbref_names:
    max_team = None; max_value = float("-inf")
    for whoscored_name in whoscored_names:
        value = get_lcs_length(fbref_name, whoscored_name)
        if value > max_value:
            max_value = value
            max_team = whoscored_name

    whoscored_names.remove(max_team)
    names_mapping[max_team] = fbref_name


outputf_file = f"{data_path}{season}/{league}/names_mapping.json"
with open(outputf_file, 'w') as f:
    json.dump(names_mapping, f)

print(f"Saved file in {outputf_file}")
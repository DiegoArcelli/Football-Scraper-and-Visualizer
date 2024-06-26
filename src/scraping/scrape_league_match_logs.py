import argparse
from utils.download_league_match_logs import get_league_match_logs

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--data_path', default="./../../datasets/", type=str)
args = parser.parse_args()

get_league_match_logs(
    root_dir=args.data_path,
    league_name=args.league,
    season=args.season,
    all_comps=args.all_comps
)

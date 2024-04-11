import argparse
from utils.download_teams_data import get_league_data
from utils.collect_data import collect_league_data, collect_season_data

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--data_path', default="./../../datasets/", type=str)
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()

get_league_data(
    root_dir=args.data_path,
    league_name=args.league,
    season=args.season,
    all_comps=args.all_comps
)

collect_league_data(
    root_dir=args.data_path,
    league_name=args.league,
    season=args.season,
    all_comps=args.all_comps
)

collect_season_data(
    root_dir=args.data_path,
    league_name=args.league,
    season=args.season,
    all_comps=args.all_comps
)

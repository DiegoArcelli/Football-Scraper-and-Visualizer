import argparse
from utils.download_league_match_logs import get_league_match_logs
from default_arguments import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--team', default=DEFAULT_TEAM, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
args = parser.parse_args()

get_league_match_logs(
    root_dir=args.data_path,
    league_name=args.league,
    season=args.season,
    team=args.team,
    all_comps=args.all_comps
)

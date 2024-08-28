import argparse
from utils.download_league_match_centre import get_league_match_centre
from default_arguments import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--team', default=DEFAULT_TEAM, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
args = parser.parse_args()

get_league_match_centre(
    root_dir=args.data_path,
    league_name=args.league,
    team=args.team,
    season=args.season,
)

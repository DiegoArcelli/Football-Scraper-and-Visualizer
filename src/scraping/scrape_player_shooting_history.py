import argparse
from utils.download_player_shooting_history import get_shooting_history
from default_arguments import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
parser.add_argument('--player_id', default=DEFAULT_PLAYER_ID, type=str)
args = parser.parse_args()

get_shooting_history(
    root_dir=args.data_path,
    player_id=args.player_id,
    league_name=args.league,
    season=args.season
)

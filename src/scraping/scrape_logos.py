import argparse
from utils import *
import time
import shutil
from utils.download_team_logos import get_league_team_logos
from default_arguments import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--team', default=DEFAULT_TEAM, type=str)
parser.add_argument('--logos_path', default=DEFAULT_LOGOS_PATH, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
args = parser.parse_args()

get_league_team_logos(
    data_dir=args.data_path,
    logos_dir=args.logos_path,
    league_name=args.league,
    season=args.season,
    team=args.team,
)
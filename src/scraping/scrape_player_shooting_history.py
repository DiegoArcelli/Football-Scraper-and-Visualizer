import argparse
from utils.download_player_shooting_history import get_shooting_history

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--data_path', default="./../../datasets/", type=str)
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--player_id', default="79443529", type=str)
args = parser.parse_args()

get_shooting_history(
    root_dir=args.data_path,
    player_id=args.player_id,
    league_name=args.league,
    season=args.season
)

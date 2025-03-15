import argparse
from utils.download_fbref_teams_data import get_league_data
# from utils.collect_data import collect_league_data, collect_season_data
from default_arguments import *
from utils.utils import ScrapeArgs
from pathlib import Path

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default=DEFAULT_LEAGUE, type=str)
parser.add_argument('--season', default=DEFAULT_SEASON, type=str)
parser.add_argument('--data_path', default=DEFAULT_DATA_PATH, type=str)
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()

data = ScrapeArgs(
    root_dir=Path(args.data_path),
    league_name=args.league,
    season=args.season,
    all_comps=args.all_comps
)

get_league_data(data)

# collect_league_data(
#     root_dir=args.data_path,
#     league_name=args.league,
#     season=args.season,
#     all_comps=args.all_comps
# )

# collect_season_data(
#     root_dir=args.data_path,
#     league_name=args.league,
#     season=args.season,
#     all_comps=args.all_comps
# )

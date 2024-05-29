import argparse
from utils.db_utils import create_databases

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--dataset_dir', default="./../../datasets/", type=str)
parser.add_argument('--database_dir', default="./../../databases/", type=str)
parser.add_argument('--team', default=None, type=str)
parser.add_argument('--league', default=None, type=str)
parser.add_argument('--season', default=None, type=str)
args = parser.parse_args()

create_databases(
    database_dir=args.database_dir,
    dataset_dir=args.dataset_dir,
    season=args.season,
    league=args.league,
    team=args.team
)
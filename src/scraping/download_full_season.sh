if [ $# -eq 0 ]; then
    season="2023-2024"
else
    season="$1"
fi

leagues=("Serie-A" "Premier-League" "La-Liga" "Bundesliga" "Ligue-1" "Champions-League")
leagues=("Serie-A" "Premier-League")

for league in "${leagues[@]}"
do 
    echo -e "\n\nDownloading $league data"
    python3 download_teams_data.py --league $league --season $season
done


#for league in "${leagues[@]}"
#do 
#    echo -e "\n\nDownloading all competitions $league data"
#    python3 download_teams_data.py --league $league --season $season --al_comps
#done


for league in "${leagues[@]}"
do 
    python3 collect_league_data.py --league $league --season $season
#    python3 collect_league_data.py --league $league --season $season --all_comps
done

python3 collect_season_data.py --season $season
#python3 collect_season_data.py --season $season --all_comps

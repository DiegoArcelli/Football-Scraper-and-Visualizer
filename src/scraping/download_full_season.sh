if [ $# -eq 0 ]; then
    season="2023-2024"
else
    season="$1"
fi

leagues=("Serie-A" "Premier-League" "La-Liga" "Bundesliga" "Ligue-1") #"Champions-League")
# leagues=("La-Liga" "Bundesliga" "Ligue-1" "Champions-League")

for league in "${leagues[@]}"
do 
    # echo -e "\n\nDownloading $league data"
    python3 scrape_teams_data.py --league $league --season $season
done


for league in "${leagues[@]}"
do 
    python3 collect_data.py --collect league  --league $league --season $season
done

python3 collect_data.py --collect season --season $season

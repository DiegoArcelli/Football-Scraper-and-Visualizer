# FBRef URL Format

League page format:

``https://fbref.com/en/comps/{league_id}/{season}/{league_name}-Stats``

For instance for Serie A (which has league ID 11) in 2022-2023 season:

``https://fbref.com/en/comps/11/2022-2023/Serie-A-Stats``

Team page format for a given competition:

``https://fbref.com/en/squads/{team_id}/{season}/c{league_id}/{team_name}-Stats-{league-name}``

For instance if we want the page for Inter in the 2021-2022 Champions league:

``https://fbref.com/en/squads/d609edc0/2021-2022/c8/Internazionale-Stats-Champions-League``

Team page format for all competitions:
``https://fbref.com/en/squads/{team_id}/{season}/all_comps/{team_name}-Stats-{league-name}``

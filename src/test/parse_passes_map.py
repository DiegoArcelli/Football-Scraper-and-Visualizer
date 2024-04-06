from bs4 import BeautifulSoup

def compare_pass(pass_1, pass_2):
    x1, y1, info1 = pass_1
    player_1 = info1["player"]
    minute_1 = info1["minute"]
    team_1 = info1["team"]
    outcome_1 = info1["outcome"]

    x2, y2, info2 = pass_2
    player_2 = info2["player"]
    minute_2 = info2["minute"]
    team_2 = info2["team"]
    outcome_2 = info2["outcome"]

    if (x1, y1, player_1, minute_1, team_1) == (x2, y2, player_2, minute_2, team_2) and outcome_1 != outcome_2:
        return True

    return False



def find_and_delete(lines, point):
    for i in range(len(lines)):

        if lines[:2] == point:
            break

    found = lines[i]

    lines = lines[:i] + lines[i+1:]
    return found, lines
    

def clean_string(string):

    for i in range(len(string)):
        if string[i] not in [" ", "\n"]:
            break
    for j in reversed(range(len(string))):
        if string[j] not in [" ", "\n"]:
            break

    return string[i:j+1]



with open("parse_map/passes", "r") as f:
    text = f.read()

soup = BeautifulSoup(text, 'html.parser')
lines = soup.select("line")
lines_list = []
for line in lines:
    x1 = line.get("x1")
    x2 = line.get("x2")
    y1 = line.get("y1")
    y2 = line.get("y2")
    lines_list.append((x1, y1, x2, y2))

lines_list.sort(key=lambda x: x[:2])




circles = soup.select("g")
circles = [circle for circle in circles if circle.get("transform") is not None]

shots = []
for circle in circles:

    if "Opta-Player"  not in circle.get("class"):
        continue

    info = circle.select("text[class='Opta-Hidden']")

    if info != []:
        info = info[0]
        outcome = info.select("span[class='Opta-Tooltip-Key']")[0].text
        minute = info.select("span[class='Opta-Tooltip-Value']")[0].text
        player = info.select("p")[0].text
        team = info.select("p")[1].text
        
        outcome = clean_string(outcome)
        minute = clean_string(minute)[:-1]
        player = clean_string(player)
        team = clean_string(team)

        shots_info = {
            "player": player,
            "outcome": outcome,
            "minute": minute,
            "team": team
        }

        pos = circle.get("transform")
        x, y = pos[10:-1].split(",")
        shots.append((x, y, shots_info))


shots.sort(key=lambda x: x[:2])


for shot in shots:
    print(shot)
    break


shots_info = []
for shot in shots:
    x1, y1, info = shot
    coord, lines_list = find_and_delete(lines_list, (x1, y1))
    _, _, x2, y2 = coord

    shots_info.append((x1, y1, x2, y2, info))





file_content="x_start,y_start,x_end,y_end,player,team,minute,outcome\n"
for shot in shots_info:
    x1, y1, x2, y2, info = shot
    player = info["player"]
    team = info["team"]
    outcome = info["outcome"]
    minute = info["minute"]
    file_content += f"{x1},{y1},{x2},{y2},{player},{team},{minute},{outcome}\n"

print(len(shots_info))
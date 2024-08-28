import pandas as pd
import matplotlib.pyplot as plt
import json
from mplsoccer import Pitch, VerticalPitch, FontManager, Sbopen

path = "./../../../datasets/2024-2025/Serie-A/matchlogs/Juventus/match_2/match_events.csv"
df = pd.read_csv(path)

for x in df["satisfied_events"]:
    json.loads(x.replace("'", '"'))

exit()
df = df[(df["type"] == "Pass") & (df["team_name"] == "Juventus")]
# passes_df = df[df["player_name"] == "Kenan Yildiz"]
passes_df = df[df["player_name"] == "Manuel Locatelli"]

pitch = Pitch(pitch_type='opta')  # example plotting an Opta/ Stats Perform pitch
fig, ax = pitch.draw()


print(len(passes_df))
for _pass in passes_df.itertuples():

    x = _pass.x; y = _pass.y; end_x = _pass.end_x; end_y = _pass.end_y
    # is_long_pass = False
    # qualifiers = _pass.qualifiers.replace("'", '"')
    # for qualifier in json.loads(qualifiers):
    #     if qualifier["type"]["displayName"] == "Longball":
    #         is_long_pass = True
    #         break

    # if not is_long_pass:
    #     continue
    dx = end_x - x
    dy = end_y - y

    if _pass.outcome_value == 1:
        plt.arrow(x, y, dx, dy, head_width=1, head_length=1, fc='green', ec='green')
    else:
        plt.arrow(x, y, dx, dy, head_width=1, head_length=1, fc='red', ec='red')

    # start_point = (x, y)
    # end_point = (end_x, end_y)
    # print(start_point, end_point)
    # x_values = [start_point[0], end_point[0]]
    # y_values = [start_point[1], end_point[1]]
    # plt.plot(x_values, y_values, 'bo', linestyle="--")
    # plt.scatter(end_x, end_y)
plt.title("Passes")
plt.show()
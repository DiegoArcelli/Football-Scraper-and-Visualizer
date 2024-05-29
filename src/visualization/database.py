import sqlite3
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot


class DataBase:


    def __init__(self, data):
        self.season = data["season"]
        self.leagues = data["leagues"]
        self.x_axis = data["x_axis"]
        self.y_axis = data["y_axis"]



    def execute_query(self):

        season = self.season.replace("-", "_").upper()
        table_names = [f"TEAM_{league.replace('-', '_').upper()}_{season}" for league in self.leagues]
        conn = sqlite3.connect(f"./../../databases/football.db")
        cursor = conn.cursor()


        teams = []; x_axis = []; y_axis = []
        for table_name in table_names:

            query = f"SELECT team, {self.x_axis}, {self.y_axis} from {table_name}"

            print(f"Executing query {query}")

            cursor.execute(query)
            results = cursor.fetchall()

            league_teams = []; league_x_axis = []; league_y_axis = []
            for (team, x, y) in results:
                league_teams.append(team)
                league_x_axis.append(x)
                league_y_axis.append(y)

            teams = teams + league_teams
            x_axis = x_axis + league_x_axis
            y_axis = y_axis + league_y_axis

            result = {
                "teams": teams,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "x_axis_label": self.x_axis,
                "y_axis_label": self.y_axis
            }

        vis = Visualizer(result)
        return vis.scatter_plot("CULoooo")


class Visualizer:


    def __init__(self, data):
        self.data = data

    def scatter_plot(
        self,
        title,
        show_avg=True,
    ):

        x_column = self.data["x_axis_label"]
        y_column = self.data["y_axis_label"]

        x_data = self.data["x_axis"]
        y_data = self.data["y_axis"]

        x_data = np.array(x_data)
        y_data = np.array(y_data)

        x_avg = x_data.mean()
        y_avg = y_data.mean()

        scatter_plot = go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            hoverinfo='text',
        )


        layout = go.Layout(
            title=title,
            xaxis=dict(title=x_column),
            yaxis=dict(title=y_column),
            font=dict(size=15)
        )

        fig = go.Figure(data=[scatter_plot], layout=layout)

        fig.update_traces(
            marker=dict(
                size=8,
                line=dict(
                    width=2,
                    color='DarkSlateGrey'
                )
            ), 
            selector=dict(mode='markers'))

        # fig.update_layout(
        #     template=annotation_template,
        #     annotations=annotations
        # )

        if show_avg:
            fig.add_vline(x=x_avg, line_width=1, line_dash="dash")
            fig.add_hline(y=y_avg, line_width=1, line_dash="dash")

        html_code = plot(fig, output_type='div')
        return html_code
        # fig.show()

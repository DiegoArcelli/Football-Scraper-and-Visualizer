import sqlite3
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot


class DataBase:


    def __init__(self, data):
        for key in data.keys():
            setattr(DataBase, key, data[key])
        print(self.x_label)


    def execute_query(self):

        season = self.season.replace("-", "_").upper()
        table_names = [f"TEAM_{league.replace('-', '_').upper()}_{season}" for league in self.leagues]
        conn = sqlite3.connect(f"./../../databases/football.db")
        cursor = conn.cursor()


        teams = []; x_axis = []; y_axis = []
        for table_name in table_names:

            if self.x_norm_attr == "":
                x_attr = self.x_axis
            else:
                x_attr = f"{self.x_axis}/{self.x_norm_attr}*{self.x_norm_quant}"


            if self.y_norm_attr == "":
                y_attr = self.y_axis
            else:
                y_attr = f"{self.y_axis}/{self.y_norm_attr}*{self.y_norm_quant}"
                

            query = f"SELECT team, {x_attr}, {y_attr} from {table_name}"

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
                "x_axis_label": self.x_label,
                "y_axis_label": self.y_label,
                "title": self.title
            }

        vis = Visualizer(result)
        return vis.scatter_plot()


class Visualizer:


    def __init__(self, data):
        self.data = data

    def scatter_plot(
        self,
        show_avg=True,
    ):

        title = self.data["title"]
        teams = self.data["teams"]

        x_column = self.data["x_axis_label"]
        y_column = self.data["y_axis_label"]

        x_data = self.data["x_axis"]
        y_data = self.data["y_axis"]

        x_data = np.array(x_data)
        y_data = np.array(y_data)

        x_avg = x_data.mean()
        y_avg = y_data.mean()

        annotation_template = go.layout.Template()
        annotation_template.layout.annotationdefaults = dict(font=dict(color="white", size=12))

        annotations = [
            dict(
                text=self.data["teams"][i],
                x=x_data[i],
                y=y_data[i],
                #ay=0.1
            ) for i in range(len(x_data))
        ]


        text = [f"Team: {teams[i]}<br>{x_column}: {x_data[i]}<br>{y_column}: {y_data[i]}" for i in range(len(teams))]
        scatter_plot = go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            text=text,
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

        fig.update_layout(
            template=annotation_template,
            annotations=annotations
        )

        fig.update_annotations(
            font=dict(color="white"),
            bgcolor="DarkSlateGrey",
            arrowcolor="DarkSlateGrey",
            bordercolor="black",
            arrowhead=2,
        )

        if show_avg:
            fig.add_vline(x=x_avg, line_width=1, line_dash="dash")
            fig.add_hline(y=y_avg, line_width=1, line_dash="dash")

        html_code = plot(fig, output_type='div')
        return html_code
        # fig.show()

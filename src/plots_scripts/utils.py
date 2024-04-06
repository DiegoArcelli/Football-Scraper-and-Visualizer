import plotly.graph_objects as go
from PIL import Image

def scatter_plot(
    data,
    x_column,
    y_column,
    text,
    annotation_column,
    data_to_annotate,
    title,
    x_label,
    y_label,
    show_avg=True,
    images=False,
    annotation_position=None
):
    x_data = data[x_column]
    y_data = data[y_column]

    x_avg = x_data.mean()
    y_avg = y_data.mean()

    to_annotate = data[data[annotation_column].isin(data_to_annotate)]
    print(to_annotate)

    annotation_template = go.layout.Template()
    annotation_template.layout.annotationdefaults = dict(font=dict(color="white", size=12))

    if annotation_position is None:
        annotations = [
            dict(
                text=to_annotate[annotation_column].iloc[i],
                x=to_annotate[x_column].iloc[i],
                y=to_annotate[y_column].iloc[i],
                #ay=0.1
            ) for i in range(len(to_annotate))
        ]
    else:
        annotations = [
            dict(
                text=to_annotate[annotation_column].iloc[i],
                x=to_annotate[x_column].iloc[i],
                y=to_annotate[y_column].iloc[i],
                xref="x",
                yref="y",
                ax=-10 if to_annotate[annotation_column].iloc[i] not in annotation_position.keys() else annotation_position[to_annotate[annotation_column].iloc[i]][0],
                ay=-30 if to_annotate[annotation_column].iloc[i] not in annotation_position.keys() else annotation_position[to_annotate[annotation_column].iloc[i]][1]
                #ay=0.1
            ) for i in range(len(to_annotate))
        ]

    if not images:
        scatter_plot = go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            text=text,
            hoverinfo='text',
        )
    else:
        scatter_plot = go.Scatter(
            x=x_data,
            y=y_data,
            text=text,
            hoverinfo='text',
        )


    layout = go.Layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        font=dict(size=15)
    )

    fig = go.Figure(data=[scatter_plot], layout=layout)

    if images:
        fig.update_traces(marker_color="rgba(0,0,0,0)")
        for i in range(len(data)):
            fig.add_layout_image(
                dict(
                    source=Image.open(f"./../../images/{data['team'][i]}.png"),
                    xref="x",
                    yref="y",
                    xanchor="center",
                    yanchor="middle",
                    x=x_data[i],
                    y=y_data[i],
                    sizex=0.025,
                    sizey=0.025,
                    sizing="contain",
                    opacity=0.8,
                    #layer="above"
                )
            )
    else:
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


    fig.show()

import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
    annotation_position=None,
    colors=None
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

    scatter_plot = go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        text=text,
        hoverinfo='text',
        marker=dict(color=colors)
    )

    layout = go.Layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        font=dict(size=15)
    )

    fig = go.Figure(data=[scatter_plot], layout=layout)

    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(
                width=1,
                #color='DarkSlateGrey'
                color="black"
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


def parallel_coordinates(data, colors, attributes):
    n_colors = len(colors)
    scales = [x/(n_colors-1) for x in range(n_colors)]
    colorscale = list(zip(scales, colors))
    print(colors)
    print(colorscale)

    fig = go.Figure(data=
        go.Parcoords(
            line = dict(
                color = colors,
                colorscale = colorscale
                #colorscale = [[0,'purple'],[0.5,'lightseagreen'],[1,'gold']]
            ),

            dimensions = [
                dict(
                    label=attribute,
                    values=data[attribute]
                ) for attribute in attributes
            ]
    
            
            # dimensions = list([
            #     dict(range = [0,8],
            #         constraintrange = [4,8],
            #         label = 'Sepal Length', values = df['sepal_length']),
            #     dict(range = [0,8],
            #         label = 'Sepal Width', values = df['sepal_width']),
            #     dict(range = [0,8],
            #         label = 'Petal Length', values = df['petal_length']),
            #     dict(range = [0,8],
            #         label = 'Petal Width', values = df['petal_width'])
            # ])
        )
    )

    fig.update_layout(
        plot_bgcolor = 'white',
        paper_bgcolor = 'white'
    )

    fig.show()


def radar_plot(data, attributes, n_clusters):
    fig = go.Figure()

    for k in range(n_clusters):
        fig.add_trace(go.Scatterpolar(
            r = data.iloc[k].tolist(),
            theta=attributes,
            fill='toself',
            name=f"Cluster {k}"
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True,
            #range=[0, 5]
            )),
        showlegend=True
    )

    fig.show()


def get_bar_plots_grid(data, num_clusters, n_cols=3):
    n_rows = int(num_clusters/n_cols) + 1

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=[f"Players for roles in cluster {k}" for k in range(num_clusters)]
    )
    row, col = 1, 1
    for k in range(num_clusters):
        roles, counts = data[k]
        fig.add_trace(go.Bar(x=roles, y=counts), row=row, col=col)
        col += 1
        if col == n_cols + 1:
            col = 1
            row += 1 
    fig.show()
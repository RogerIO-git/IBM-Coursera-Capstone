# Import required libraries
import pandas as pd
# import dash
# from dash import html
# from dash import dcc
from dash import Dash, html, dcc, Input, Output
# from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

launch_sites = []
launch_sites.append({'label': 'All Sites', 'value': 'All Sites'})
for item in spacex_df["Launch Site"].value_counts().index:
    launch_sites.append({'label': item, 'value': item})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown', options = launch_sites, value = 'All Sites', placeholder = "Select a Launch Site here", searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min = 0, max = 10000, step = 1000, value = [min_payload, max_payload], marks={ 2500: {'label': '2500 (Kg)'}, 5000: {'label': '5000 (Kg)'}, 7500: {'label': '7500 (Kg)'}}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))
def select(input):
    if input == 'All Sites':
        new_df = spacex_df.groupby(['Launch Site'])['class'].sum().reset_index()

        graph1 = px.pie(
            new_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        site_df = spacex_df[spacex_df["Launch Site"] == input]

        success = (site_df["class"] == 1).sum()
        failure = (site_df["class"] == 0).sum()
        new_df = pd.DataFrame({
            'Outcome': ['Failure', 'Success'],
            'Count': [failure, success]
        })
        graph1 = px.pie(
            new_df,
            values='Count',
            names='Outcome',
            title='Total Successful Launches for ' + input
        )
    return graph1

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def scatter(input1, input2):

    print("Selected site:", input1)
    print("Payload range:", input2)

    # Start with the complete dataframe
    filtered_df = spacex_df.copy()

    # Filter by launch site
    if input1 != 'All Sites':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == input1
        ]

    # Filter by payload
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= input2[0]) &
        (filtered_df['Payload Mass (kg)'] <= input2[1])
    ]

    print("Rows after filtering:", len(filtered_df))

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload Mass vs. Launch Success'
    )

    return fig
    

# Run the app
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=8050,
        debug=True,
        use_reloader=False
    )
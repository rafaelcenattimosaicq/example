# Import necessary libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch data into a pandas DataFrame
launch_data = pd.read_csv("spacex_launch_dash.csv")
min_weight = launch_data['Payload Mass (kg)'].min()
max_weight = launch_data['Payload Mass (kg)'].max()

# Initialize the Dash app
dash_app = dash.Dash(__name__)

# Define the layout of the app
dash_app.layout = html.Div(children=[
    html.H1("SpaceX Launch Records Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown to select launch site
    dcc.Dropdown(
        id='launch-site-selector',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        placeholder='Select a Launch Site',
        value='ALL',
        searchable=True
    ),
    html.Br(),

    # Pie chart to display launch outcomes
    html.Div(dcc.Graph(id='launch-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Slider for selecting payload range
    dcc.RangeSlider(
        id='weight-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_weight, max_weight]
    ),

    # Scatter chart for payload vs. launch outcome
    html.Div(dcc.Graph(id='launch-scatter-chart'))
])

# Callback to update the pie chart based on the selected launch site
@dash_app.callback(
    Output(component_id='launch-pie-chart', component_property='figure'),
    Input(component_id='launch-site-selector', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group data by launch site and count only successful launches (class == 1)
        success_summary = launch_data[launch_data['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
        fig = px.pie(success_summary, values='Success Count', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # Filter data for the selected launch site
        site_data = launch_data[launch_data['Launch Site'] == selected_site]
        # Calculate success and failure counts
        success_count = site_data['class'].sum()
        failure_count = len(site_data) - success_count
        outcome_df = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Count': [success_count, failure_count]
        })
        fig = px.pie(outcome_df, values='Count', names='Outcome',
                     title=f'Launch Outcome Breakdown for {selected_site}')
    return fig

# Callback to update the scatter chart based on the selected launch site and payload range
@dash_app.callback(
    Output(component_id='launch-scatter-chart', component_property='figure'),
    [Input(component_id='launch-site-selector', component_property='value'),
     Input(component_id='weight-slider', component_property='value')]
)
def update_scatter_chart(selected_site, weight_range):
    low, high = weight_range
    if selected_site == 'ALL':
        filtered_data = launch_data[(launch_data['Payload Mass (kg)'] >= low) & 
                                    (launch_data['Payload Mass (kg)'] <= high)]
        chart_title = 'Payload vs. Launch Outcome for All Sites'
    else:
        filtered_data = launch_data[(launch_data['Launch Site'] == selected_site) &
                                    (launch_data['Payload Mass (kg)'] >= low) & 
                                    (launch_data['Payload Mass (kg)'] <= high)]
        chart_title = f'Payload vs. Launch Outcome for {selected_site}'
    
    fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', hover_data=['Launch Site'],
                     title=chart_title)
    return fig

# Run the app
if __name__ == '__main__':
    dash_app.run_server()

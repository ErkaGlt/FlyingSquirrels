
import sqlite3
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# Connect to the SQLite database
db_path = "HBOMax_Content.db"
conn = sqlite3.connect(db_path)

# Fetch data for the different graphs
# Subscriber Growth by Streaming Platform
query_subscriber_growth = """
    SELECT StreamingPlatform, Region, COUNT(SubscriberID) AS SubscriberCount
    FROM Subscribers
    GROUP BY StreamingPlatform, Region
"""
subscriber_growth_data = pd.read_sql_query(query_subscriber_growth, conn)

# Genre Preferences of Taiwanese Viewers
query_genre_preferences = """
    SELECT Genre, Language, Views
    FROM Content
    WHERE Language = 'Mandarin'
"""
genre_preferences_data = pd.read_sql_query(query_genre_preferences, conn)

# Campaign Effectiveness
query_campaign_effectiveness = """
    SELECT CampaignName, Impressions, Clicks, Conversion
    FROM MarketingCampaigns
"""
campaign_effectiveness_data = pd.read_sql_query(query_campaign_effectiveness, conn)

# User Complaints
query_user_complaints = """
    SELECT Date, UserComplaints
    FROM PlatformMetrics
"""
user_complaints_data = pd.read_sql_query(query_user_complaints, conn)

# Ensure UserComplaints is numeric
user_complaints_data['UserComplaints'] = pd.to_numeric(user_complaints_data['UserComplaints'], errors='coerce')

conn.close()

# Initialize the Dash App
app = Dash(__name__)
server = app.server

# App Layout
app.layout = html.Div(
    style={
        'backgroundColor': '#2c2c2c',
        'color': 'white',
        'fontFamily': 'Arial, sans-serif',
        'padding': '10px',
        'height': 'auto',
        'overflowY': 'auto'  # Enable vertical scrolling
    },
    children=[
        # Title Bar
        html.Div(
            style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '10px 20px',
                'backgroundColor': '#444',
                'borderRadius': '5px',
                'marginBottom': '20px'
            },
            children=[
                html.H1(
                    "HBO MAX Asian Market Expansion Dashboard",
                    style={
                        'color': 'white',
                        'margin': '0',
                        'fontSize': '28px',
                        'textAlign': 'center'
                    }
                ),
                html.Div(
                    style={
                        'display': 'flex',
                        'gap': '10px'
                    },
                    children=[
                        html.Div(
                            "Region: All Regions",
                            style={
                                'color': 'white',
                                'padding': '5px 10px',
                                'backgroundColor': '#555',
                                'borderRadius': '3px'
                            }
                        ),
                        html.Div(
                            "Time Frame: Monthly",
                            style={
                                'color': 'white',
                                'padding': '5px 10px',
                                'backgroundColor': '#555',
                                'borderRadius': '3px'
                            }
                        )
                    ]
                )
            ]
        ),
        # Dashboard Grid
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateRows': 'auto auto',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '10px'
            },
            children=[
                # Row 1: Subscriber Growth and Genre Preferences
                html.Div(
                    children=[
                        html.H3("Subscriber Growth by Streaming Platform", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='region-dropdown',
                            options=[
                                {'label': 'All Regions', 'value': 'All'}
                            ] + [{'label': region, 'value': region} for region in subscriber_growth_data['Region'].unique()],
                            value='All',
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='subscriber-growth-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #444', 'padding': '10px'}
                ),
                html.Div(
                    children=[
                        html.H3("Genre Preferences of Taiwanese Viewers", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='language-dropdown',
                            options=[{'label': lang, 'value': lang} for lang in genre_preferences_data['Language'].unique()],
                            value=genre_preferences_data['Language'].unique()[0],
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='genre-preferences-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #444', 'padding': '10px'}
                ),
                # Row 2: Campaign Effectiveness and User Complaints
                html.Div(
                    children=[
                        html.H3("Campaign Effectiveness", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='campaign-dropdown',
                            options=[{'label': campaign, 'value': campaign} for campaign in campaign_effectiveness_data['CampaignName'].unique()],
                            value=campaign_effectiveness_data['CampaignName'].unique()[0],
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='campaign-effectiveness-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #444', 'padding': '10px'}
                ),
                html.Div(
                    children=[
                        html.H3("User Complaints", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='date-dropdown',
                            options=[{'label': str(date), 'value': str(date)} for date in user_complaints_data['Date'].unique()],
                            value=str(user_complaints_data['Date'].min()),
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='user-complaints-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #444', 'padding': '10px'}
                )
            ]
        )
    ]
)


# Callbacks for Interactivity
@app.callback(
    Output('subscriber-growth-chart', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_subscriber_growth(selected_region):
    if selected_region == 'All':
        filtered_data = subscriber_growth_data
    else:
        filtered_data = subscriber_growth_data[subscriber_growth_data['Region'] == selected_region]

    fig = go.Figure()
    for platform in filtered_data['StreamingPlatform'].unique():
        platform_data = filtered_data[filtered_data['StreamingPlatform'] == platform]
        fig.add_trace(
            go.Bar(
                x=platform_data['SubscriberCount'],
                y=[platform],
                orientation='h',
                name=platform
            )
        )
    fig.update_layout(barmode='stack', title="Subscriber Growth", paper_bgcolor='#2c2c2c', plot_bgcolor='#2c2c2c', font=dict(color='white'))
    return fig

@app.callback(
    Output('genre-preferences-chart', 'figure'),
    [Input('language-dropdown', 'value')]
)
def update_genre_preferences(selected_language):
    filtered_data = genre_preferences_data[genre_preferences_data['Language'] == selected_language]

    # Unique colors for each genre
    genres = filtered_data['Genre'].unique()
    colors = [
        '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
        '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
    ]
    genre_colors = {genre: colors[i % len(colors)] for i, genre in enumerate(genres)}

    fig = go.Figure()
    for genre in genres:
        genre_data = filtered_data[filtered_data['Genre'] == genre]
        fig.add_trace(
            go.Bar(
                x=genre_data['Views'],
                y=[genre],
                orientation='h',
                marker_color=genre_colors[genre],
                name=genre
            )
        )

    fig.update_layout(
        title="Number of Views by Genre",
        paper_bgcolor='#2c2c2c',
        plot_bgcolor='#2c2c2c',
        font=dict(color='white'),
        barmode='stack',
        legend=dict(
            title="Genre",
            orientation="v",
            x=1.02,  # Position outside the chart area
            y=1,
            bgcolor="#2c2c2c",
            bordercolor="white",
            borderwidth=1
        )
    )
    return fig


@app.callback(
    Output('campaign-effectiveness-chart', 'figure'),
    [Input('campaign-dropdown', 'value')]
)
def update_campaign_effectiveness(selected_campaign):
    filtered_data = campaign_effectiveness_data[campaign_effectiveness_data['CampaignName'] == selected_campaign]
    fig = go.Figure(
        data=[
            go.Funnel(
                y=['Impressions', 'Clicks', 'Conversion'],
                x=[
                    filtered_data['Impressions'].iloc[0],
                    filtered_data['Clicks'].iloc[0],
                    int(filtered_data['Conversion'].iloc[0])
                ]
            )
        ]
    )
    fig.update_layout(title="Campaign Effectiveness", paper_bgcolor='#2c2c2c', plot_bgcolor='#2c2c2c', font=dict(color='white'))
    return fig

@app.callback(
    Output('user-complaints-chart', 'figure'),
    [Input('date-dropdown', 'value')]
)
def update_user_complaints(selected_date):
    filtered_data = user_complaints_data[user_complaints_data['Date'] == selected_date]
    average_complaints = filtered_data['UserComplaints'].mean()
    fig = go.Figure(
        data=[
            go.Indicator(
                mode="gauge+number",
                value=average_complaints,
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 20], 'color': "green"},
                        {'range': [20, 40], 'color': "yellow"},
                        {'range': [40, 60], 'color': "orange"},
                        {'range': [60, 100], 'color': "red"}
                    ]
                }
            )
        ]
    )
    fig.update_layout(title="User Complaints (%)", paper_bgcolor='#2c2c2c', plot_bgcolor='#2c2c2c', font=dict(color='white'))
    return fig

# Run the App
if __name__ == '__main__':
    app.run(debug=True)
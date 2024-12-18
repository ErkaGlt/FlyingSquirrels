# -*- coding: utf-8 -*-
"""18-Dec.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IOi5U573gTrONFcqE0g6QLfTgsT-8zFo
"""

import sqlite3
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

db_path = "HBOMax_Content.db"
conn = sqlite3.connect(db_path)

query_subscriber_growth = """
    SELECT DATE(SubscriptionDate) AS SubscriptionDate, Region, COUNT(DISTINCT SubscriberID) AS SubscriberCount
    FROM Subscribers
    GROUP BY DATE(SubscriptionDate), Region
"""
subscriber_growth_data = pd.read_sql_query(query_subscriber_growth, conn)
subscriber_growth_data['SubscriptionDate'] = pd.to_datetime(subscriber_growth_data['SubscriptionDate'])
subscriber_growth_data['Month'] = subscriber_growth_data['SubscriptionDate'].dt.to_period('M').astype(str)

query_genre_preferences = """
    SELECT c.Genre, c.Language, c.Views
    FROM Content AS c
    JOIN ContentRegionMapping AS crm
    ON c.ContentID = crm.ContentID
    WHERE crm.Region = 'Taiwan'
"""
genre_preferences_data = pd.read_sql_query(query_genre_preferences, conn)

query_subscriber_diversity = """
    SELECT Region AS Country, COUNT(DISTINCT SubscriberID) AS SubscriberCount
    FROM Subscribers
    WHERE Region IN ('China', 'India', 'Japan', 'Indonesia', 'Malaysia', 'Myanmar', 'Philippines',
                     'Singapore', 'Taiwan', 'Thailand', 'Vietnam', 'Korea', 'Pakistan')
    GROUP BY Region
"""
subscriber_diversity_data = pd.read_sql_query(query_subscriber_diversity, conn)

query_campaign_effectiveness = """
    SELECT CampaignName, Impressions, Clicks, Conversion
    FROM MarketingCampaigns
"""
campaign_effectiveness_data = pd.read_sql_query(query_campaign_effectiveness, conn)

query_user_complaints = """
    SELECT Date, UserComplaints
    FROM PlatformMetrics
"""
user_complaints_data = pd.read_sql_query(query_user_complaints, conn)
user_complaints_data['UserComplaints'] = pd.to_numeric(user_complaints_data['UserComplaints'], errors='coerce')

conn.close()

app = Dash(__name__)
server = app.server

# App Layout
app.layout = html.Div(
    style={
        'backgroundColor': 'black',
        'color': 'white',
        'fontFamily': 'Arial, sans-serif',
        'padding': '10px',
        'height': 'auto',
        'overflowY': 'auto'
    },
    children=[

        html.Div(
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'padding': '10px 20px',
                'backgroundColor': '#333',
                'borderRadius': '5px',
                'marginBottom': '20px'
            },
            children=[
                html.H1(
                    "HBO MAX Asian Market Expansion Dashboard",
                    style={'color': 'white', 'margin': '0', 'fontSize': '28px'}
                )
            ]
        ),

        html.Div(
            style={
                'display': 'grid',
                'gridTemplateRows': 'auto auto',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '10px'
            },
            children=[

                html.Div(
                    children=[
                        html.H3("Subscriber Growth by Region", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='month-filter',
                            options=[{'label': month, 'value': month} for month in subscriber_growth_data['Month'].unique()],
                            value='2024-01',
                            #value=subscriber_growth_data['Month'].max(),
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='growth-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #555', 'padding': '10px', 'backgroundColor': '#111'}
                ),

                html.Div(
                    children=[
                        html.H3("Genre Preferences in Taiwan", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='language-dropdown',
                            options=[{'label': lang, 'value': lang} for lang in genre_preferences_data['Language'].unique()],
                            #value=genre_preferences_data['Language'].unique()[0],
                            value='Mandarin',
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='genre-preferences-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #555', 'padding': '10px', 'backgroundColor': '#111'}
                ),

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
                    style={'border': '1px solid #555', 'padding': '10px', 'backgroundColor': '#111'}
                ),

                html.Div(
                    children=[
                        html.H3("User Complaints Gauge Chart", style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='date-dropdown',
                            options=[{'label': str(date), 'value': str(date)} for date in user_complaints_data['Date'].unique()],
                            value=str(user_complaints_data['Date'].min()),
                            style={'color': 'black'}
                        ),
                        dcc.Graph(id='user-complaints-chart', style={'height': '300px'})
                    ],
                    style={'border': '1px solid #555', 'padding': '10px', 'backgroundColor': '#111'}
                )
            ]
        ),

        html.Div(
            children=[
                html.H3("Subscriber Diversity by Asian Countries", style={'textAlign': 'center', 'marginTop': '20px'}),
                dcc.Graph(id='subscriber-diversity-map', style={'height': '600px'})
            ],
            style={'border': '1px solid #555', 'padding': '10px', 'backgroundColor': '#111'}
        )
    ]
)
@app.callback(
    Output('growth-chart', 'figure'),
    Input('month-filter', 'value')
)
def update_growth_chart(selected_month):

    filtered_data = subscriber_growth_data[subscriber_growth_data['Month'] == selected_month]
    regional_data = filtered_data.groupby('Region')['SubscriberCount'].sum().reset_index()


    fig = px.bar(
        regional_data,
        x='Region',
        y='SubscriberCount',
        color='SubscriberCount',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='black',
        font=dict(color='white'),
        coloraxis_colorbar=dict(
            title="Subscriber Count",
            tickfont=dict(color='white'),
            titlefont=dict(color='white')
        )
    )
    return fig

@app.callback(
    Output('genre-preferences-chart', 'figure'),
    Input('language-dropdown', 'value')
)
def update_genre_preferences(selected_language):

    filtered_data = genre_preferences_data[genre_preferences_data['Language'] == selected_language]


    fig = px.bar(
        filtered_data,
        x='Genre',
        y='Views',
        title=f"Genre Preferences in Taiwan: {selected_language}",
        color='Views',
        color_continuous_scale='Blues',
        template='plotly_dark'
    )
    fig.update_layout(
        paper_bgcolor='black',
        font=dict(color='white'),
        coloraxis_colorbar=dict(
            title="Views",
            tickfont=dict(color='white'),
            titlefont=dict(color='white')
        )
    )
    return fig

@app.callback(
    Output('campaign-effectiveness-chart', 'figure'),
    Input('campaign-dropdown', 'value')
)
def update_campaign_effectiveness(selected_campaign):

    filtered_data = campaign_effectiveness_data[campaign_effectiveness_data['CampaignName'] == selected_campaign]


    if filtered_data.empty or filtered_data[['Impressions', 'Clicks', 'Conversion']].isnull().any().any():
        return go.Figure().update_layout(
            title="No data available for selected campaign",
            paper_bgcolor='black',
            font=dict(color='white')
        )


    blue_gradient = ['#FFFFFF', '#1E90FF', '#00008B']


    fig = go.Figure(
        go.Funnel(
            y=['Impressions', 'Clicks', 'Conversion'],
            x=[
                filtered_data['Impressions'].iloc[0],
                filtered_data['Clicks'].iloc[0],
                filtered_data['Conversion'].iloc[0]
            ],
            textinfo="value+percent initial",
            marker=dict(color=blue_gradient)
        )
    )
    fig.update_layout(
        title=f"Campaign Effectiveness: {selected_campaign}",
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white'),
        yaxis=dict(
            title=dict(text="Stages", font=dict(color='white')),
            tickfont=dict(color='white')
        ),
        xaxis=dict(
            title=dict(text="Value", font=dict(color='white')),
            tickfont=dict(color='white')
        )
    )
    return fig



@app.callback(
    Output('user-complaints-chart', 'figure'),
    Input('date-dropdown', 'value')
)
def update_user_complaints(selected_date):
    # Filter data for the selected date
    filtered_data = user_complaints_data[user_complaints_data['Date'] == selected_date]
    average_complaints = filtered_data['UserComplaints'].mean()

    # Create the gauge chart
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=average_complaints,
            title={'text': "Average User Complaints", 'font': {'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'color': 'white'}},
                'steps': [
                    {'range': [0, 20], 'color': "green"},
                    {'range': [20, 40], 'color': "yellow"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 100], 'color': "red"}
                ],
                'bar': {'color': "black"}
            }
        )
    )

    fig.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white")
    )
    return fig
@app.callback(Output('subscriber-diversity-map', 'figure'), Input('subscriber-diversity-map', 'id'))
def update_subscriber_map(_):
    return px.choropleth(
        subscriber_diversity_data, locations='Country', locationmode='country names',
        color='SubscriberCount', hover_name='Country', color_continuous_scale='Viridis'
    )
# Run the App
if __name__ == '__main__':
    app.run(debug=True)


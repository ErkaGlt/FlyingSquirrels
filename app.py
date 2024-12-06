import sqlite3
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Step 1: Connect to SQLite Database and Load Data
db_path = "ContentEngagementDB.db"
conn = sqlite3.connect(db_path)

# Fetch data from the database
query = "SELECT * FROM Subscribers;" 
subscribers_data = pd.read_sql_query(query, conn)
conn.close()

# Step 2: Ensure the 'SubscriptionDate' column is parsed as dates
subscribers_data['SubscriptionDate'] = pd.to_datetime(subscribers_data['SubscriptionDate'], errors='coerce')

# Step 3: Aggregate cumulative subscriber growth over time
cumulative_growth = (
    subscribers_data.groupby('SubscriptionDate').size().cumsum().reset_index(name='CumulativeSubscribers')
)

# Step 4: Initialize the Dash app
app = Dash(__name__)
server = app.server

# Step 5: Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Subscriber Growth Dashboard", style={'textAlign': 'center'}),

    # Date Picker Range for filtering
    html.Label("Select Date Range:"),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=cumulative_growth['SubscriptionDate'].min(),
        end_date=cumulative_growth['SubscriptionDate'].max(),
        display_format='YYYY-MM-DD'
    ),

    # Line graph for subscriber growth
    dcc.Graph(id='subscriber-growth-graph')
])

# Step 6: Define callback to update the graph based on selected date range
@app.callback(
    Output('subscriber-growth-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_graph(start_date, end_date):
    # Filter data based on the selected date range
    filtered_data = cumulative_growth[
        (cumulative_growth['SubscriptionDate'] >= start_date) &
        (cumulative_growth['SubscriptionDate'] <= end_date)
    ]
    
    # Create the line chart
    fig = px.line(
        filtered_data,
        x='SubscriptionDate',
        y='CumulativeSubscribers',
        title="Subscriber Growth Over Time",
        labels={'SubscriptionDate': 'Date', 'CumulativeSubscribers': 'Cumulative Subscribers'}
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Subscribers")
    
    return fig

# Step 7: Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)

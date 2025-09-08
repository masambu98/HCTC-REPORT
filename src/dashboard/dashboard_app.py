"""
Professional Dashboard Application for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

Enterprise-grade analytics dashboard with real-time updates,
advanced filtering, and comprehensive reporting.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so `import src.*` works even when invoked as
# `python src/dashboard/dashboard_app.py` (Render runs this form).
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import logging

from src.config import config
from src.services import get_message_service
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create Dash application
app = dash.Dash(__name__)
app.title = "HCTC-CRM Analytics Dashboard - Signature: 8598"

# Get message service
message_service = get_message_service()


def load_messages() -> pd.DataFrame:
    """Load messages from database with error handling."""
    try:
        messages = message_service.get_messages(limit=10000)
        
        if not messages:
            return pd.DataFrame(columns=[
                'id', 'agent', 'platform', 'recipient', 'content', 'timestamp', 
                'message_type', 'message_id', 'sender_id', 'is_incoming', 'status', 'extra_data'
            ])
        
        # Convert to DataFrame
        data = [msg.to_dict() for msg in messages]
        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load messages: {e}")
        return pd.DataFrame()


def create_layout() -> html.Div:
    """Create the main dashboard layout."""
    return html.Div([
        # Header
        html.Div([
            html.H1("HCTC-CRM Analytics Dashboard"),
            html.P("Professional Call Center Management - Signature: 8598"),
            html.Div(id='last-updated', className='updated-at', style={'textAlign': 'right'})
        ], className='hctc-header', style={'padding': '16px 20px', 'marginBottom': '20px', 'borderRadius': '10px'}),
        
        # Control Panel
        html.Div([
            html.Div([
                html.Label("Platform Filter", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='platform-filter',
                    options=[
                        {'label': 'All Platforms', 'value': 'all'},
                        {'label': 'WhatsApp', 'value': 'WhatsApp'},
                        {'label': 'Facebook', 'value': 'Facebook'},
                    ],
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], style={'flex': '1 1 200px', 'minWidth': '200px', 'marginRight': '12px'}),
            
            html.Div([
                html.Label("Agent Filter", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='agent-filter',
                    options=[{'label': 'All Agents', 'value': 'all'}],
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], style={'flex': '1 1 200px', 'minWidth': '200px', 'marginRight': '12px'}),
            
            html.Div([
                html.Label("Date Range", style={'fontWeight': 'bold'}),
                dcc.DatePickerRange(
                    id='date-range',
                    minimum_nights=0,
                    start_date=date.today() - timedelta(days=7),
                    end_date=date.today(),
                    style={'width': '100%'}
                ),
            ], style={'flex': '1 1 260px', 'minWidth': '260px', 'marginRight': '12px'}),
            
            html.Div([
                html.Label("Search Messages", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='search-text',
                    type='text',
                    placeholder='Search content, recipient, agent...',
                    debounce=True,
                    style={'width': '100%'}
                ),
            ], style={'flex': '2 1 300px', 'minWidth': '300px', 'marginRight': '12px'}),
            
            html.Div([
                html.Label("Message Type", style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='message-type-filter',
                    options=[
                        {'label': 'Incoming Only', 'value': 'incoming'},
                        {'label': 'Outgoing Only', 'value': 'outgoing'},
                    ],
                    value=['incoming'],
                    style={'marginTop': '5px'}
                ),
            ], style={'flex': '1 1 200px'}),
        ], className='hctc-controls', style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px', 
                 'padding': '16px'}),
        
        # Action Buttons
        html.Div([
            html.Button('🔄 Refresh Data', id='refresh-btn', n_clicks=0,
                       className='btn btn-refresh',
                       style={'marginRight': '10px'}),
            html.Button('📊 Export CSV', id='export-btn', n_clicks=0,
                       className='btn btn-export',
                       style={'marginRight': '10px'}),
            html.Button('📈 Generate Report', id='report-btn', n_clicks=0,
                       className='btn btn-report'),
            dcc.Download(id='download-csv'),
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),
        
        # Statistics Cards
        html.Div([
            html.Div([
                html.H3(id='total-messages', children='0', style={'margin': '0'}),
                html.P('Total Messages', style={'margin': '5px 0 0 0'})
            ], className='hctc-card', style={'textAlign': 'center', 'padding': '20px', 'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                html.H3(id='incoming-messages', children='0', style={'margin': '0', 'color': '#58a618'}),
                html.P('Incoming', style={'margin': '5px 0 0 0'})
            ], className='hctc-card', style={'textAlign': 'center', 'padding': '20px', 'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                html.H3(id='outgoing-messages', children='0', style={'margin': '0', 'color': '#dc2626'}),
                html.P('Outgoing', style={'margin': '5px 0 0 0'})
            ], className='hctc-card', style={'textAlign': 'center', 'padding': '20px', 'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                html.H3(id='active-agents', children='0', style={'margin': '0', 'color': '#7c3aed'}),
                html.P('Active Agents', style={'margin': '5px 0 0 0'})
            ], className='hctc-card', style={'textAlign': 'center', 'padding': '20px', 'flex': '1'}),
        ], className='hctc-stats', style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
        
        # Charts Row
        html.Div([
            # Platform Distribution Chart
            html.Div([
                html.H4("Platform Distribution", style={'textAlign': 'center', 'marginBottom': '20px'}),
                dcc.Graph(id='platform-chart', config={'displayModeBar': False}, style={'height': '280px'})
            ], className='hctc-panel', style={'flex': '1 1 48%', 'maxWidth': '48%', 'minWidth': '300px', 'marginRight': '10px', 'padding': '20px'}),
            
            # Agent Performance Chart
            html.Div([
                html.H4("Agent Performance", style={'textAlign': 'center', 'marginBottom': '20px'}),
                dcc.Graph(id='agent-chart', config={'displayModeBar': False}, style={'height': '280px'})
            ], className='hctc-panel', style={'flex': '1 1 48%', 'maxWidth': '48%', 'minWidth': '300px', 'padding': '20px'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'marginBottom': '20px'}),
        
        # Messages Table
        html.Div([
            html.H4("Message History", style={'marginBottom': '20px'}),
            dash_table.DataTable(
                id='messages-table',
                columns=[
                    {'name': 'ID', 'id': 'id', 'type': 'numeric'},
                    {'name': 'Timestamp', 'id': 'timestamp', 'type': 'datetime'},
                    {'name': 'Platform', 'id': 'platform'},
                    {'name': 'Agent', 'id': 'agent'},
                    {'name': 'Recipient', 'id': 'recipient'},
                    {'name': 'Type', 'id': 'message_type'},
                    {'name': 'Content', 'id': 'content', 'presentation': 'markdown'},
                    {'name': 'Status', 'id': 'status'},
                    {'name': 'Direction', 'id': 'is_incoming', 'type': 'text'},
                ],
                data=[],
                page_size=15,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'fontFamily': 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
                    'fontSize': '13px',
                    'padding': '10px'
                },
                style_header={
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{is_incoming} = true'},
                        'backgroundColor': '#ecfdf5',
                    },
                    {
                        'if': {'filter_query': '{is_incoming} = false'},
                        'backgroundColor': '#fef2f2',
                    }
                ]
            )
        ], className='hctc-table', style={'padding': '20px'}),
        
        # Auto-refresh interval
        dcc.Interval(
            id='refresh-interval',
            interval=30 * 1000,  # 30 seconds
            n_intervals=0
        ),
        
        # Footer
        html.Div([
            html.P("© 2025 HCTC-CRM Professional Call Center Management - Signature: 8598", 
                  style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '20px 0 0 0'})
        ])
    ], className='hctc-container', style={'padding': '20px', 'minHeight': '100vh'})


# Set the layout
app.layout = create_layout()


def apply_filters(df: pd.DataFrame, platform: str, agent: str, start_date: date, 
                 end_date: date, search_text: str, message_types: List[str]) -> pd.DataFrame:
    """Apply filters to the dataframe."""
    if df.empty:
        return df
    
    filtered = df.copy()
    
    # Platform filter
    if platform and platform != 'all':
        filtered = filtered[filtered['platform'] == platform]
    
    # Agent filter
    if agent and agent != 'all':
        filtered = filtered[filtered['agent'] == agent]
    
    # Date range filter
    if start_date:
        filtered = filtered[filtered['timestamp'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered['timestamp'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]
    
    # Search filter
    if search_text:
        search_term = search_text.lower()
        filtered = filtered[
            filtered[['content', 'recipient', 'agent']].fillna('')
            .apply(lambda row: search_term in (row['content'].lower() + ' ' + 
                                            row['recipient'].lower() + ' ' + 
                                            row['agent'].lower()), axis=1)
        ]
    
    # Message type filter
    if message_types:
        if 'incoming' in message_types and 'outgoing' in message_types:
            pass  # Show all
        elif 'incoming' in message_types:
            filtered = filtered[filtered['is_incoming'] == True]
        elif 'outgoing' in message_types:
            filtered = filtered[filtered['is_incoming'] == False]
    
    return filtered.sort_values(by='timestamp', ascending=False)


# Callbacks
@app.callback(
    [Output('messages-table', 'data'),
     Output('total-messages', 'children'),
     Output('incoming-messages', 'children'),
     Output('outgoing-messages', 'children'),
     Output('active-agents', 'children'),
     Output('platform-chart', 'figure'),
     Output('agent-chart', 'figure')],
    [Input('refresh-interval', 'n_intervals'),
     Input('refresh-btn', 'n_clicks'),
     Input('platform-filter', 'value'),
     Input('agent-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('search-text', 'value'),
     Input('message-type-filter', 'value')]
)
def update_dashboard(n_intervals, refresh_clicks, platform, agent, start_date, 
                    end_date, search_text, message_types):
    """Update dashboard with filtered data."""
    try:
        # Load data
        df = load_messages()
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", 
                                   x=0.5, y=0.5, showarrow=False)
            return [], "0", "0", "0", "0", empty_fig, empty_fig
        
        # Update agent filter options
        agent_options = [{'label': 'All Agents', 'value': 'all'}]
        agent_options.extend([{'label': ag, 'value': ag} for ag in df['agent'].unique()])
        
        # Apply filters
        filtered_df = apply_filters(
            df, platform or 'all', agent or 'all',
            pd.to_datetime(start_date).date() if start_date else None,
            pd.to_datetime(end_date).date() if end_date else None,
            search_text or '', message_types or []
        )
        
        # Prepare table data
        table_data = filtered_df.copy()
        if 'timestamp' in table_data.columns:
            table_data['timestamp'] = table_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        table_data['is_incoming'] = table_data['is_incoming'].map({True: 'Incoming', False: 'Outgoing'})
        
        # Calculate statistics
        total_messages = len(filtered_df)
        incoming_count = len(filtered_df[filtered_df['is_incoming'] == True])
        outgoing_count = len(filtered_df[filtered_df['is_incoming'] == False])
        active_agents = len(filtered_df['agent'].unique())
        
        # Cisco color palette for charts
        CISCO_COLORS = ['#00bceb', '#0d274d', '#58a618', '#7c3aed', '#dc2626', '#0284c7', '#14b8a6', '#f59e0b']

        # Platform chart
        platform_counts = filtered_df['platform'].value_counts()
        platform_fig = px.pie(
            values=platform_counts.values,
            names=platform_counts.index,
            title="Message Distribution by Platform",
            color_discrete_sequence=CISCO_COLORS
        )
        platform_fig.update_layout(
            showlegend=True,
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial', size=13),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Agent chart
        agent_counts = filtered_df['agent'].value_counts()
        bar_colors = [CISCO_COLORS[i % len(CISCO_COLORS)] for i in range(len(agent_counts))]
        agent_fig = go.Figure(data=[
            go.Bar(x=list(agent_counts.index), y=list(agent_counts.values), marker_color=bar_colors)
        ])
        agent_fig.update_layout(
            title_text="Messages by Agent",
            showlegend=False,
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial', size=13),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return (table_data.to_dict('records'), str(total_messages), 
                str(incoming_count), str(outgoing_count), str(active_agents),
                platform_fig, agent_fig)
        
    except Exception as e:
        logger.error(f"Dashboard update error: {e}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error loading data", xref="paper", yref="paper", 
                               x=0.5, y=0.5, showarrow=False)
        return [], "0", "0", "0", "0", empty_fig, empty_fig


@app.callback(
    Output('download-csv', 'data'),
    [Input('export-btn', 'n_clicks')],
    [State('platform-filter', 'value'),
     State('agent-filter', 'value'),
     State('date-range', 'start_date'),
     State('date-range', 'end_date'),
     State('search-text', 'value'),
     State('message-type-filter', 'value')],
    prevent_initial_call=True
)
def export_csv(n_clicks, platform, agent, start_date, end_date, search_text, message_types):
    """Export filtered data to CSV."""
    if n_clicks is None:
        return None
    
    try:
        df = load_messages()
        filtered_df = apply_filters(
            df, platform or 'all', agent or 'all',
            pd.to_datetime(start_date).date() if start_date else None,
            pd.to_datetime(end_date).date() if end_date else None,
            search_text or '', message_types or []
        )
        
        filename = f"hctc_crm_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return dcc.send_data_frame(filtered_df.to_csv, filename, index=False)
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return None


if __name__ == '__main__':
    logger.info("Starting HCTC-CRM Dashboard - Signature: 8598")
    app.run(
        host=config.dashboard.host,
        port=config.dashboard.port,
        debug=config.dashboard.debug
    )


# Last Updated timestamp updater
@app.callback(
    Output('last-updated', 'children'),
    [Input('refresh-interval', 'n_intervals'), Input('refresh-btn', 'n_clicks')]
)
def update_last_updated(_, __):
    try:
        return f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception:
        return "Last Updated: --"

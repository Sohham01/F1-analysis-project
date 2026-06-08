import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import data_loader as dl

# Set Page Config
st.set_page_config(page_title="Race Weekend Deep-Dive | F1 Analytics", page_icon="🏎️", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="f1-header">
    <div class="f1-title">Race Weekend Deep-Dive</div>
    <div class="f1-subtitle">Analyze race results, lap-by-lap telemetry, pit stop performance, and position changes.</div>
</div>
""", unsafe_allow_html=True)

# Load data
races_df = dl.get_races()
results_df = dl.get_results_merged()
pit_stops_df = dl.get_pit_stops_merged()
status_df = dl.get_status_mapping()

# Season & Grand Prix Selector in Sidebar
st.sidebar.header("Select Race")
available_years = sorted(races_df['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Year", available_years, index=0)

year_races = races_df[races_df['year'] == selected_year].sort_values(by='round')
race_names = year_races['name'].tolist()

if len(race_names) > 0:
    selected_race_name = st.sidebar.selectbox("Grand Prix", race_names)
    selected_race_row = year_races[year_races['name'] == selected_race_name].iloc[0]
    race_id = selected_race_row['raceId']
    
    # Header Info
    circuit_id = selected_race_row['circuitId']
    circuits_df = dl.get_circuits()
    circ_info = circuits_df[circuits_df['circuitId'] == circuit_id].iloc[0]
    
    st.markdown(f"### {selected_race_name} - {selected_year}")
    st.markdown(f"**Venue:** {circ_info['name']} ({circ_info['location']}, {circ_info['country']}) | **Date:** {selected_race_row['date'].strftime('%d %b %Y')}")
    
    # Get race results
    race_results = results_df[results_df['raceId'] == race_id].sort_values(by='positionOrder')
    
    # Merge status for DNF explanations
    race_results = race_results.merge(status_df, on='statusId', how='left')
    
    # Display Race Classification
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Official Classification</h4>
    </div>
    """, unsafe_allow_html=True)
    
    classification_df = race_results[['positionOrder', 'number', 'driver_name', 'constructor_name', 'grid', 'laps', 'time', 'status', 'points']].copy()
    classification_df.columns = ['Pos', 'No', 'Driver', 'Team', 'Grid', 'Laps', 'Time/Retired', 'Status', 'Points']
    
    # If the time is NaN, fill it with the status (e.g. Spun off, Collision)
    classification_df['Time/Retired'] = classification_df['Time/Retired'].fillna(classification_df['Status'])
    classification_df = classification_df.drop(columns=['Status'])
    
    st.dataframe(classification_df, use_container_width=True, hide_index=True)
    
    # Tabs for analytics
    tab1, tab2, tab3 = st.tabs(["🏎️ Lap Pace Analysis", "🔧 Pit Stop Analytics", "📊 Grid vs. Finish Changes"])
    
    with tab1:
        st.markdown("#### Lap-by-Lap Pace Comparison")
        st.write("Compare the race pace of different drivers lap by lap. Select up to 4 drivers to compare their lap telemetry.")
        
        try:
            lap_times = dl.get_lap_times_for_race(race_id)
            
            if not lap_times.empty:
                drivers_in_race = sorted(lap_times['driver_name'].unique().tolist())
                # Default select top 2 finishers
                default_drivers = classification_df['Driver'].head(2).tolist()
                default_drivers = [d for d in default_drivers if d in drivers_in_race]
                
                selected_drivers = st.multiselect("Select Drivers to Compare", drivers_in_race, default=default_drivers)
                
                if len(selected_drivers) > 0:
                    filtered_laps = lap_times[lap_times['driver_name'].isin(selected_drivers)].copy()
                    
                    # Convert milliseconds to seconds
                    filtered_laps['lap_time_secs'] = filtered_laps['milliseconds'] / 1000.0
                    
                    # Line plot
                    fig_laps = px.line(
                        filtered_laps,
                        x='lap',
                        y='lap_time_secs',
                        color='driver_name',
                        labels={'lap': 'Lap Number', 'lap_time_secs': 'Lap Time (seconds)', 'driver_name': 'Driver'},
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.qualitative.Set1
                    )
                    
                    fig_laps.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        yaxis=dict(title='Lap Time (seconds)'),
                        margin=dict(l=0, r=0, t=10, b=0),
                        height=400
                    )
                    st.plotly_chart(fig_laps, use_container_width=True)
                else:
                    st.warning("Please select at least one driver to plot the lap times.")
            else:
                st.info("Lap times telemetry is not available for this race (data typically starts around 1996).")
        except Exception as e:
            st.error(f"Error loading lap times: {e}")
            
    with tab2:
        st.markdown("#### Pit Stop Analysis")
        
        # Filter pit stops for this race
        race_pit_stops = pit_stops_df[pit_stops_df['raceId'] == race_id].copy()
        
        if not race_pit_stops.empty:
            col_tbl, col_chart = st.columns([1, 1])
            
            with col_tbl:
                st.markdown("**Pit Stop Records**")
                display_pit = race_pit_stops[['stop', 'lap', 'driver_name', 'time', 'duration']].sort_values(by=['lap', 'stop'])
                display_pit.columns = ['Stop No', 'Lap', 'Driver', 'Time of Day', 'Duration (s)']
                st.dataframe(display_pit, use_container_width=True, hide_index=True, height=300)
                
            with col_chart:
                st.markdown("**Average Pit Stop Duration by Constructor**")
                
                # Merge with constructor name
                pit_with_team = race_pit_stops.merge(race_results[['driver_name', 'constructor_name']], on='driver_name', how='left')
                avg_pit_team = pit_with_team.groupby('constructor_name')['duration'].mean().reset_index()
                avg_pit_team = avg_pit_team.sort_values(by='duration')
                
                fig_pit = px.bar(
                    avg_pit_team,
                    x='duration',
                    y='constructor_name',
                    orientation='h',
                    labels={'duration': 'Average Duration (seconds)', 'constructor_name': 'Constructor'},
                    color='duration',
                    color_continuous_scale='Reds',
                    template="plotly_dark"
                )
                
                fig_pit.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=300
                )
                st.plotly_chart(fig_pit, use_container_width=True)
        else:
            st.info("Pit stop duration analysis is not available for this race (data typically starts around 2011).")
            
    with tab3:
        st.markdown("#### Starting Grid vs. Finishing Classification")
        st.write("Compare where drivers started on the grid versus where they finished classification. Above the diagonal line means they gained positions; below means they lost positions.")
        
        # Scatter plot grid vs finishing position
        # Filter out grid=0 (which usually indicates pit lane starts, let's treat it as starting 21st or exclude)
        scatter_data = race_results[race_results['grid'] > 0].copy()
        
        # Make a column for tooltip
        scatter_data['gain_loss'] = scatter_data['positions_gained'].apply(lambda x: f"+{x}" if x > 0 else str(x))
        
        fig_scatter = px.scatter(
            scatter_data,
            x='grid',
            y='positionOrder',
            hover_name='driver_name',
            hover_data={'constructor_name': True, 'grid': True, 'positionOrder': True, 'gain_loss': True},
            labels={'grid': 'Starting Grid Position', 'positionOrder': 'Finishing Classification Position'},
            template="plotly_dark",
            size_max=12
        )
        
        # Add diagonal reference line (y = x)
        max_val = max(scatter_data['grid'].max(), scatter_data['positionOrder'].max())
        fig_scatter.add_shape(
            type="line",
            x0=1, y0=1, x1=max_val, y1=max_val,
            line=dict(color="gray", width=1.5, dash="dash")
        )
        
        fig_scatter.update_traces(marker=dict(size=12, color='#ff1801', symbol='circle'))
        
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            height=400,
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(tickmode='linear', tick0=1, dtick=1)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.error("No races found for the selected year.")

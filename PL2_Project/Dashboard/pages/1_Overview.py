import os
import streamlit as st
import plotly.express as px
import pandas as pd
import data_loader as dl

# Set Page Config
st.set_page_config(page_title="Season Overview | F1 Analytics", page_icon="🏎️", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="f1-header">
    <div class="f1-title">Season Overview & Standings</div>
    <div class="f1-subtitle">Track the progression and final results of any Formula 1 season.</div>
</div>
""", unsafe_allow_html=True)

# Load data
races = dl.get_races()
driver_standings = dl.get_driver_standings_merged()
constructor_standings = dl.get_constructor_standings_merged()
results = dl.get_results_merged()

# Sidebar controls
st.sidebar.header("Season Selector")
available_years = sorted(races['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Season", available_years)

# Filter data for selected year
year_races = races[races['year'] == selected_year].sort_values(by='round')
year_results = results[results['year'] == selected_year]
year_driver_standings = driver_standings[driver_standings['year'] == selected_year]
year_constructor_standings = constructor_standings[constructor_standings['year'] == selected_year]

# Basic Year Stats
num_races = len(year_races)
st.markdown(f"### Season {selected_year} Summary ({num_races} Grands Prix)")

# Display standings inside columns
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Driver Standings</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if len(year_driver_standings) > 0:
        # Find the latest round in driver standings for this year
        latest_round = year_driver_standings['round'].max()
        final_driver_standings = year_driver_standings[year_driver_standings['round'] == latest_round].sort_values(by='position')
        
        display_ds = final_driver_standings[['position', 'driver_name', 'code', 'points', 'wins']].reset_index(drop=True)
        display_ds.columns = ['Pos', 'Driver', 'Code', 'Points', 'Wins']
        st.dataframe(display_ds, use_container_width=True, hide_index=True)
    else:
        st.info("No driver standings data found for this season.")

with col_right:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Constructor Standings</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if len(year_constructor_standings) > 0:
        latest_round = year_constructor_standings['round'].max()
        final_constructor_standings = year_constructor_standings[year_constructor_standings['round'] == latest_round].sort_values(by='position')
        
        display_cs = final_constructor_standings[['position', 'constructor_name', 'points', 'wins']].reset_index(drop=True)
        display_cs.columns = ['Pos', 'Constructor', 'Points', 'Wins']
        st.dataframe(display_cs, use_container_width=True, hide_index=True)
    else:
        st.info("No constructor standings data found for this season (not introduced until 1958).")

# Visualizations section
st.markdown("### Season Progression & Analytics")

# Plotly Line Chart for Driver Points Progression
st.markdown("""
<div class="glass-container">
    <h4 style="color:#ffffff; margin-top:0;">Points Progression throughout the Season</h4>
    <p style="color:#94a3b8; font-size:0.85rem;">See how the championship battle unfolded round by round. Only the top 8 drivers are shown for clarity.</p>
</div>
""", unsafe_allow_html=True)

if len(year_driver_standings) > 0:
    # Filter top 8 drivers of the season
    latest_round = year_driver_standings['round'].max()
    top_drivers = year_driver_standings[year_driver_standings['round'] == latest_round].sort_values(by='position').head(8)['driver_name'].tolist()
    
    progression_df = year_driver_standings[year_driver_standings['driver_name'].isin(top_drivers)].sort_values(by=['round'])
    
    fig_line = px.line(
        progression_df,
        x='round',
        y='points',
        color='driver_name',
        labels={'round': 'Round / Race Number', 'points': 'Total Points', 'driver_name': 'Driver'},
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Alphabet
    )
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Progression data not available for this season.")

# Additional stats: Race wins breakdown
col_w, col_l = st.columns([2, 1])

with col_w:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Race Victories by Driver</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if len(year_results) > 0:
        winners = year_results[year_results['positionOrder'] == 1]['driver_name'].value_counts().reset_index()
        winners.columns = ['Driver', 'Wins']
        
        fig_wins = px.bar(
            winners,
            x='Wins',
            y='Driver',
            orientation='h',
            color='Wins',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_wins.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300
        )
        st.plotly_chart(fig_wins, use_container_width=True)
    else:
        st.info("No race results data found for this year.")

with col_l:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Race Calendar</h4>
    </div>
    """, unsafe_allow_html=True)
    
    calendar_df = year_races[['round', 'name', 'date']].reset_index(drop=True)
    calendar_df.columns = ['Round', 'Grand Prix', 'Date']
    calendar_df['Date'] = calendar_df['Date'].dt.strftime('%d %b %Y')
    st.dataframe(calendar_df, use_container_width=True, hide_index=True, height=260)

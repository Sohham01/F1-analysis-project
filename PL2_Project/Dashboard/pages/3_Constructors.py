import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import data_loader as dl

# Set Page Config
st.set_page_config(page_title="Constructor Analytics | F1 Analytics", page_icon="🏎️", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="f1-header">
    <div class="f1-title">Constructor Analytics & Teammate Battles</div>
    <div class="f1-subtitle">Track team performance trends across seasons and analyze head-to-head teammate battles.</div>
</div>
""", unsafe_allow_html=True)

# Load data
constructors_df = dl.get_constructors()
results_df = dl.get_results_merged()
qualifying_df = dl.get_qualifying_merged()
constructor_summary_df = dl.get_constructor_summary()
races_df = dl.get_races()

# Sort constructor list
constructors_list = constructors_df.sort_values(by='constructor_name')

st.markdown("### Constructor Profile & History")

# Select constructor
selected_const_name = st.selectbox("Select a Constructor", constructors_list['constructor_name'].unique())
selected_const_row = constructors_df[constructors_df['constructor_name'] == selected_const_name].iloc[0]
const_id = selected_const_row['constructorId']

# Display quick profile info
col_c1, col_c2 = st.columns([1, 2])

with col_c1:
    # Get precomputed summary stats if available
    summary_row = constructor_summary_df[constructor_summary_df['constructor_name'] == selected_const_name]
    
    if len(summary_row) > 0:
        total_races = int(summary_row.iloc[0]['races'])
        total_points = float(summary_row.iloc[0]['points'])
        avg_finish = float(summary_row.iloc[0]['avg_finish'])
    else:
        # Compute on the fly if not in precomputed summary
        const_results = results_df[results_df['constructorId'] == const_id]
        total_races = const_results['raceId'].nunique()
        total_points = const_results['points'].sum()
        avg_finish = const_results['positionOrder'].mean()
        
    st.markdown(f"""
    <div class="glass-container">
        <h4 style="color:#ff1801; margin-top:0; margin-bottom:5px;">{selected_const_name}</h4>
        <p style="margin-bottom:8px;"><b>Nationality:</b> {selected_const_row['nationality']}</p>
        <p style="margin-bottom:8px;"><b>Total GP Entries:</b> {total_races}</p>
        <p style="margin-bottom:8px;"><b>Total Points:</b> {total_points:.1f}</p>
        <p style="margin-bottom:8px;"><b>Average Finish:</b> {avg_finish:.2f}</p>
        <p style="margin-bottom:0;"><a href="{selected_const_row['url']}" target="_blank" style="color:#ff1801; text-decoration:none; font-weight:600;">Wikipedia Page ↗</a></p>
    </div>
    """, unsafe_allow_html=True)

with col_c2:
    # Plot points scored across seasons
    const_season_points = results_df[results_df['constructorId'] == const_id].groupby('year')['points'].sum().reset_index()
    
    if len(const_season_points) > 0:
        fig_const = px.bar(
            const_season_points,
            x='year',
            y='points',
            labels={'year': 'Season', 'points': 'Total Points Scored'},
            color='points',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_const.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=210
        )
        st.plotly_chart(fig_const, use_container_width=True)
    else:
        st.info("No season history available.")

st.markdown("---")

# Teammate Battle Section
st.markdown("### Teammate Head-to-Head Battle")
st.write("F1 teammates are the only drivers with identical cars. This makes comparing teammate performance the ultimate metric of a driver's speed and consistency.")

# Select a season for this constructor
constructor_seasons = sorted(results_df[results_df['constructorId'] == const_id]['year'].unique(), reverse=True)

if len(constructor_seasons) > 0:
    selected_season = st.selectbox("Select Season to Analyze Teammates", constructor_seasons)
    
    # Filter results for this constructor and season
    season_results = results_df[(results_df['constructorId'] == const_id) & (results_df['year'] == selected_season)]
    season_quali = qualifying_df[(qualifying_df['constructorId'] == const_id) & (qualifying_df['year'] == selected_season)]
    
    # Get unique drivers
    drivers_in_team = season_results['driver_name'].unique().tolist()
    
    if len(drivers_in_team) >= 2:
        # Limit to top 2 drivers by race counts (in case there were guest drivers)
        driver_counts = season_results['driver_name'].value_counts()
        d1_name = driver_counts.index[0]
        d2_name = driver_counts.index[1]
        
        d1_results = season_results[season_results['driver_name'] == d1_name]
        d2_results = season_results[season_results['driver_name'] == d2_name]
        
        # Calculate stats
        d1_points = d1_results['points'].sum()
        d2_points = d2_results['points'].sum()
        
        # Head-to-head race finishes (excluding double DNFs or where someone did not start)
        races_both_finished = season_results.groupby('raceId').filter(lambda x: d1_name in x['driver_name'].values and d2_name in x['driver_name'].values)
        
        d1_ahead_race = 0
        d2_ahead_race = 0
        
        for race_id in races_both_finished['raceId'].unique():
            r1 = d1_results[d1_results['raceId'] == race_id]
            r2 = d2_results[d2_results['raceId'] == race_id]
            
            if len(r1) > 0 and len(r2) > 0:
                p1 = r1.iloc[0]['positionOrder']
                p2 = r2.iloc[0]['positionOrder']
                
                # If they both finished or even if one DNF'd, the one classified higher (lower positionOrder) gets the point
                if p1 < p2:
                    d1_ahead_race += 1
                elif p2 < p1:
                    d2_ahead_race += 1
                    
        # Head-to-head qualifying
        d1_ahead_quali = 0
        d2_ahead_quali = 0
        
        for race_id in season_quali['raceId'].unique():
            q1 = season_quali[(season_quali['raceId'] == race_id) & (season_quali['driver_name'] == d1_name)]
            q2 = season_quali[(season_quali['raceId'] == race_id) & (season_quali['driver_name'] == d2_name)]
            
            if len(q1) > 0 and len(q2) > 0:
                pos1 = q1.iloc[0]['position']
                pos2 = q2.iloc[0]['position']
                if pos1 < pos2:
                    d1_ahead_quali += 1
                elif pos2 < pos1:
                    d2_ahead_quali += 1
        
        # Display head-to-head cards
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #ff1801;">
                <div class="kpi-label">Race Finish Battle</div>
                <div class="kpi-value">{d1_ahead_race} - {d2_ahead_race}</div>
                <div class="kpi-desc">Number of times finished ahead of teammate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #ff8c00;">
                <div class="kpi-label">Qualifying Battle</div>
                <div class="kpi-value">{d1_ahead_quali} - {d2_ahead_quali}</div>
                <div class="kpi-desc">Number of times qualified ahead of teammate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t3:
            total_pts = d1_points + d2_points
            pct1 = (d1_points / total_pts * 100) if total_pts > 0 else 50
            pct2 = 100 - pct1
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #2563eb;">
                <div class="kpi-label">Points Share</div>
                <div class="kpi-value">{d1_points:.1f} pts vs {d2_points:.1f} pts</div>
                <div class="kpi-desc">Share: {d1_name} ({pct1:.1f}%) | {d2_name} ({pct2:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Detail table per race
        st.markdown("#### Race-by-Race Details")
        
        race_details = []
        for race_id in races_df[races_df['year'] == selected_season].sort_values(by='round')['raceId']:
            r_info = races_df[races_df['raceId'] == race_id].iloc[0]
            
            # Find results
            res1 = d1_results[d1_results['raceId'] == race_id]
            res2 = d2_results[d2_results['raceId'] == race_id]
            
            # Find qualifying
            q1 = season_quali[(season_quali['raceId'] == race_id) & (season_quali['driver_name'] == d1_name)]
            q2 = season_quali[(season_quali['raceId'] == race_id) & (season_quali['driver_name'] == d2_name)]
            
            grid1 = res1.iloc[0]['grid'] if len(res1) > 0 else (q1.iloc[0]['position'] if len(q1) > 0 else "-")
            finish1 = res1.iloc[0]['positionText'] if len(res1) > 0 else "-"
            
            grid2 = res2.iloc[0]['grid'] if len(res2) > 0 else (q2.iloc[0]['position'] if len(q2) > 0 else "-")
            finish2 = res2.iloc[0]['positionText'] if len(res2) > 0 else "-"
            
            race_details.append({
                "Round": int(r_info['round']),
                "Grand Prix": r_info['name'],
                f"{d1_name} Grid": grid1,
                f"{d1_name} Finish": finish1,
                f"{d2_name} Grid": grid2,
                f"{d2_name} Finish": finish2
            })
            
        details_df = pd.DataFrame(race_details)
        st.dataframe(details_df, use_container_width=True, hide_index=True)
    else:
        st.info("The selected constructor did not run at least 2 drivers in this season.")
else:
    st.info("No season records found for this team.")

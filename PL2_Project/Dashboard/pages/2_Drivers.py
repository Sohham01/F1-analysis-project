import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import data_loader as dl

# Set Page Config
st.set_page_config(page_title="Driver Analytics | F1 Analytics", page_icon="🏎️", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="f1-header">
    <div class="f1-title">Driver Analytics & Comparisons</div>
    <div class="f1-subtitle">Look up individual career stats or run a head-to-head comparison between two drivers.</div>
</div>
""", unsafe_allow_html=True)

# Load data
drivers_df = dl.get_drivers()
results_df = dl.get_results_merged()
qualifying_df = dl.get_qualifying_merged()

# Cache driver stats calculation
def calculate_driver_stats(driver_id):
    drv_results = results_df[results_df['driverId'] == driver_id]
    drv_quali = qualifying_df[qualifying_df['driverId'] == driver_id]
    
    races_started = len(drv_results)
    if races_started == 0:
        return None
        
    wins = len(drv_results[drv_results['positionOrder'] == 1])
    podiums = len(drv_results[drv_results['positionOrder'] <= 3])
    points = drv_results['points'].sum()
    
    # Poles from qualifying
    poles = len(drv_quali[drv_quali['position'] == 1])
    
    avg_finish = drv_results['positionOrder'].mean()
    avg_grid = drv_results['grid'].mean()
    
    # Rates for Radar Chart
    win_rate = (wins / races_started) * 100
    podium_rate = (podiums / races_started) * 100
    pole_rate = (poles / races_started) * 100 if len(drv_quali) > 0 else 0.0
    
    # Inverse scores for radar (so higher is better, scaled 0 to 100)
    # 1st place grid is 100, 20th place is 0
    grid_score = max(0, (21 - avg_grid) / 20 * 100)
    finish_score = max(0, (21 - avg_finish) / 20 * 100)
    
    return {
        "races_started": races_started,
        "wins": wins,
        "podiums": podiums,
        "poles": poles,
        "points": points,
        "avg_finish": avg_finish,
        "avg_grid": avg_grid,
        "win_rate": win_rate,
        "podium_rate": podium_rate,
        "pole_rate": pole_rate,
        "grid_score": grid_score,
        "finish_score": finish_score
    }

# Sidebar selection modes
st.sidebar.header("Navigation")
mode = st.sidebar.radio("Choose Mode", ["Driver Profile Lookup", "Driver Comparison"])

drivers_list = drivers_df.sort_values(by='driver_name')

if mode == "Driver Profile Lookup":
    st.markdown("### Driver Profile Lookup")
    
    # Selection
    selected_driver_name = st.selectbox("Select a Driver", drivers_list['driver_name'].unique())
    selected_driver_row = drivers_df[drivers_df['driver_name'] == selected_driver_name].iloc[0]
    driver_id = selected_driver_row['driverId']
    
    # Bio section
    col_bio, col_stats = st.columns([1, 2])
    
    with col_bio:
        st.markdown(f"""
        <div class="glass-container">
            <h4 style="color:#ff1801; margin-top:0; margin-bottom:5px;">{selected_driver_name}</h4>
            <p style="margin-bottom:8px;"><b>Nationality:</b> {selected_driver_row['nationality']}</p>
            <p style="margin-bottom:8px;"><b>Born:</b> {selected_driver_row['dob']}</p>
            <p style="margin-bottom:8px;"><b>Code:</b> {selected_driver_row['code'] if pd.notnull(selected_driver_row['code']) else 'N/A'}</p>
            <p style="margin-bottom:0;"><a href="{selected_driver_row['url']}" target="_blank" style="color:#ff1801; text-decoration:none; font-weight:600;">Wikipedia Bio ↗</a></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_stats:
        stats = calculate_driver_stats(driver_id)
        if stats:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['races_started']}</div>
                    <div class="kpi-label">Races Started</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['wins']}</div>
                    <div class="kpi-label">Wins</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['podiums']}</div>
                    <div class="kpi-label">Podiums</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("") # Spacer
            c4, c5, c6 = st.columns(3)
            with c4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['poles']}</div>
                    <div class="kpi-label">Poles</div>
                </div>
                """, unsafe_allow_html=True)
            with c5:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['points']:.1f}</div>
                    <div class="kpi-label">Career Points</div>
                </div>
                """, unsafe_allow_html=True)
            with c6:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{stats['avg_finish']:.2f}</div>
                    <div class="kpi-label">Avg Finish</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No race statistics found for this driver.")
            
    # Sub-visualizations (e.g. race wins by season)
    if stats and stats['wins'] > 0:
        st.markdown("#### Career Wins over Time")
        drv_results = results_df[(results_df['driverId'] == driver_id) & (results_df['positionOrder'] == 1)]
        wins_by_season = drv_results.groupby('year').size().reset_index(name='wins')
        
        fig = px.bar(
            wins_by_season, 
            x='year', 
            y='wins', 
            labels={'year': 'Season', 'wins': 'Victories'},
            color='wins',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("### Head-to-Head Driver Comparison")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        d1_name = st.selectbox("Select Driver 1", drivers_list['driver_name'].unique(), index=0)
        d1_id = drivers_df[drivers_df['driver_name'] == d1_name].iloc[0]['driverId']
    with col_sel2:
        # Default to a different driver (like Schumacher or Prost)
        default_index = int(np.where(drivers_list['driver_name'].unique() == "Michael Schumacher")[0][0]) if "Michael Schumacher" in drivers_list['driver_name'].unique() else 1
        d2_name = st.selectbox("Select Driver 2", drivers_list['driver_name'].unique(), index=default_index)
        d2_id = drivers_df[drivers_df['driver_name'] == d2_name].iloc[0]['driverId']
        
    if d1_id == d2_id:
        st.warning("Please select two different drivers to run a comparison.")
    else:
        stats1 = calculate_driver_stats(d1_id)
        stats2 = calculate_driver_stats(d2_id)
        
        if stats1 and stats2:
            # Let's create columns for stats comparison
            st.write("")
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown(f"""
                <div class="glass-container">
                    <h4 style="color:#ffffff; margin-top:0;">Comparison Summary</h4>
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>{d1_name}</th>
                                <th>{d2_name}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><b>Races Started</b></td>
                                <td>{stats1['races_started']}</td>
                                <td>{stats2['races_started']}</td>
                            </tr>
                            <tr>
                                <td><b>Total Wins</b></td>
                                <td>{stats1['wins']}</td>
                                <td>{stats2['wins']}</td>
                            </tr>
                            <tr>
                                <td><b>Podiums</b></td>
                                <td>{stats1['podiums']}</td>
                                <td>{stats2['podiums']}</td>
                            </tr>
                            <tr>
                                <td><b>Poles</b></td>
                                <td>{stats1['poles']}</td>
                                <td>{stats2['poles']}</td>
                            </tr>
                            <tr>
                                <td><b>Career Points</b></td>
                                <td>{stats1['points']:.1f}</td>
                                <td>{stats2['points']:.1f}</td>
                            </tr>
                            <tr>
                                <td><b>Avg. Grid Pos</b></td>
                                <td>{stats1['avg_grid']:.2f}</td>
                                <td>{stats2['avg_grid']:.2f}</td>
                            </tr>
                            <tr>
                                <td><b>Avg. Finish Pos</b></td>
                                <td>{stats1['avg_finish']:.2f}</td>
                                <td>{stats2['avg_finish']:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
            with col_right:
                st.markdown(f"""
                <div class="glass-container">
                    <h4 style="color:#ffffff; margin-top:0;">Career Performance Profile (Radar Chart)</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Radar chart plotting
                categories = ['Win Rate %', 'Podium Rate %', 'Pole Rate %', 'Qualifying Grid Score', 'Finishing Race Score']
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=[stats1['win_rate'], stats1['podium_rate'], stats1['pole_rate'], stats1['grid_score'], stats1['finish_score']],
                    theta=categories,
                    fill='toself',
                    name=d1_name,
                    line_color='#ff1801'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=[stats2['win_rate'], stats2['podium_rate'], stats2['pole_rate'], stats2['grid_score'], stats2['finish_score']],
                    theta=categories,
                    fill='toself',
                    name=d2_name,
                    line_color='#2563eb'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            color='#64748b'
                        ),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                    margin=dict(l=40, r=40, t=10, b=10),
                    height=330
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data is missing for one or both selected drivers.")

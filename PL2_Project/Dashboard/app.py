import os
import streamlit as st
import plotly.express as px
import pandas as pd
import data_loader as dl

# Set Streamlit Page Config
st.set_page_config(
    page_title="Formula 1 Analytics Hub",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="f1-header">
    <div class="f1-title">Formula 1 Analytics Hub</div>
    <div class="f1-subtitle">Interactive Dashboard for Data-Driven F1 Historical Insights & Predictions</div>
</div>
""", unsafe_allow_html=True)

# Compute global stats
try:
    drivers_df = dl.get_drivers()
    constructors_df = dl.get_constructors()
    races_df = dl.get_races()
    circuits_df = dl.get_circuits()
    
    total_seasons = races_df['year'].nunique()
    total_races = races_df['raceId'].nunique()
    total_drivers = drivers_df['driverId'].nunique()
    total_circuits = circuits_df['circuitId'].nunique()
except Exception as e:
    st.error(f"Error loading data: {e}")
    total_seasons, total_races, total_drivers, total_circuits = 0, 0, 0, 0

# Display KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_seasons}</div>
        <div class="kpi-label">Seasons</div>
        <div class="kpi-desc">F1 history from 1950 to Present</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_races}</div>
        <div class="kpi-label">Grands Prix</div>
        <div class="kpi-desc">Total races run historically</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_drivers}</div>
        <div class="kpi-label">Drivers</div>
        <div class="kpi-desc">Different drivers in F1 history</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_circuits}</div>
        <div class="kpi-label">Circuits</div>
        <div class="kpi-desc">Venues that hosted a Grand Prix</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# Main layout split: Project Intro & Global Circuit Map
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("""
    <div class="glass-container">
        <h3 style="color:#ff1801; margin-top:0;">Welcome to the F1 Analytics Hub</h3>
        <p>This interactive platform provides data-driven explorations of Formula 1 history. Built for a 2nd-semester coding and data science project, it runs entirely in Python using Pandas and Plotly, demonstrating data ingestion, cleaning, analysis, and visualization.</p>
        <h4 style="color:#ffffff;">Explore the Pages in the Sidebar:</h4>
        <ul style="color:#cbd5e1; padding-left:20px;">
            <li><b>Overview:</b> Driver and Constructor standings and race progression across seasons.</li>
            <li><b>Drivers:</b> Profiles, career stats, and head-to-head comparisons of your favorite drivers.</li>
            <li><b>Constructors:</b> Teammate battles and constructor progression.</li>
            <li><b>Race Weekend:</b> Deep-dive telemetry, lap paces, and pit stop durations.</li>
            <li><b>Predictive Analytics:</b> Use a Scikit-Learn regression model to predict finishing position based on starting grid and driver experience.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="glass-container" style="height: 100%;">
        <h3 style="color:#ffffff; margin-top:0; margin-bottom: 10px;">Global F1 Circuits Map</h3>
        <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:15px;">Hover over markers to view circuit names, locations, and altitudes. Zoom and drag to explore the globality of F1.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and clean circuit lat/lng for mapping
    try:
        # Cast lat/lng to numeric
        circuits_df['lat'] = pd.to_numeric(circuits_df['lat'], errors='coerce')
        circuits_df['lng'] = pd.to_numeric(circuits_df['lng'], errors='coerce')
        circuits_df['alt'] = pd.to_numeric(circuits_df['alt'], errors='coerce').fillna(0)
        
        # Create map
        fig = px.scatter_geo(
            circuits_df,
            lat='lat',
            lon='lng',
            hover_name='name',
            hover_data={'location': True, 'country': True, 'alt': True, 'lat': False, 'lng': False},
            color_discrete_sequence=['#ff1801'],
            projection="natural earth"
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                showland=True,
                landcolor="rgb(20, 20, 30)",
                subunitcolor="rgb(40, 40, 50)",
                countrycolor="rgb(40, 40, 50)",
                showocean=True,
                oceancolor="rgb(10, 10, 15)",
                showlakes=False,
                bgcolor="rgba(0,0,0,0)"
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating circuit map: {e}")

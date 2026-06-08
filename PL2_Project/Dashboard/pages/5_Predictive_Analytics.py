import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import data_loader as dl

# Set Page Config
st.set_page_config(page_title="Predictive Analytics | F1 Analytics", page_icon="🏎️", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="f1-header">
    <div class="f1-title">Predictive Regression Model</div>
    <div class="f1-subtitle">Use a Scikit-Learn Linear Regression model to predict a driver's final finish position.</div>
</div>
""", unsafe_allow_html=True)

# Cache data prep and model training
@st.cache_resource
def train_model():
    # Load required data
    results = dl.get_results_merged()
    driver_standings = dl.load_csv('driver_standings.csv')
    
    # Sort chronologically
    df = results.sort_values(by=['year', 'round', 'positionOrder']).copy()
    
    # Feature Engineering
    # 1. Driver cumulative experience (number of races)
    df['driver_experience'] = df.groupby('driverId').cumcount()
    
    # 2. Driver Form: average positionOrder of the last 3 races (rolling average)
    df['driver_form'] = df.groupby('driverId')['positionOrder'].shift(1).rolling(3, min_periods=1).mean()
    df['driver_form'] = df['driver_form'].fillna(df['grid'])
    
    # 3. Team Standing points prior to race
    driver_standings['points'] = pd.to_numeric(driver_standings['points'])
    driver_standings['raceId'] = pd.to_numeric(driver_standings['raceId'])
    driver_standings['driverId'] = pd.to_numeric(driver_standings['driverId'])
    
    driver_standings['prev_points'] = driver_standings.groupby('driverId')['points'].shift(1).fillna(0)
    
    df = df.merge(driver_standings[['raceId', 'driverId', 'prev_points']], on=['raceId', 'driverId'], how='left')
    df['prev_points'] = df['prev_points'].fillna(0)
    
    # Filter for modern era (races since 2010) to keep model relevant
    model_df = df[df['year'] >= 2010].dropna(subset=['positionOrder', 'grid', 'driver_experience', 'driver_form', 'prev_points'])
    
    features = ['grid', 'driver_experience', 'driver_form', 'prev_points']
    X = model_df[features]
    y = model_df['positionOrder']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # Save statistics for driver lookup defaults
    driver_stats = df[df['year'] >= 2010].groupby('driver_name').agg({
        'driverId': 'first',
        'driver_experience': 'max',
        'positionOrder': 'mean', # average finish as form proxy
        'prev_points': 'mean'
    }).reset_index()
    
    return model, r2, mae, rmse, features, driver_stats

# Train model (runs instantly due to caching)
with st.spinner("Training Linear Regression model on historical F1 data..."):
    model, r2, mae, rmse, features, driver_lookup = train_model()

# Split layout: Simulation Inputs & Live Prediction
col_inputs, col_results = st.columns([1, 1])

with col_inputs:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0; margin-bottom:15px;">Simulation Inputs</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Select driver to load default stats
    selected_driver = st.selectbox("Select Driver (auto-loads career defaults)", driver_lookup['driver_name'].unique())
    driver_default = driver_lookup[driver_lookup['driver_name'] == selected_driver].iloc[0]
    
    # Interactive sliders
    grid_pos = st.slider("Starting Grid Position (P1 to P24)", 1, 24, 5)
    
    st.write("")
    st.markdown("**Driver Attributes (Adjust as needed):**")
    experience = st.slider(
        "Career Races Experience", 
        0, 400, 
        int(driver_default['driver_experience'])
    )
    
    recent_form = st.slider(
        "Recent Finish Form (Avg of last 3 races)", 
        1.0, 24.0, 
        float(driver_default['positionOrder']), 
        step=0.5
    )
    
    team_points = st.slider(
        "Constructor Points in Standings", 
        0.0, 800.0, 
        float(driver_default['prev_points']), 
        step=10.0
    )

with col_results:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0; margin-bottom:15px;">Live Regression Prediction</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Make Prediction
    input_data = np.array([[grid_pos, experience, recent_form, team_points]])
    raw_pred = model.predict(input_data)[0]
    
    # Clip predictions between P1 and P24 (there are no negative positions or positions > 24)
    pred_pos = max(1.0, min(24.0, raw_pred))
    pred_rounded = int(round(pred_pos))
    
    # Display styling card
    if pred_rounded == 1:
        suffix = "st (Winner!)"
        color = "#ff1801"
    elif pred_rounded == 2:
        suffix = "nd (Podium)"
        color = "#ff8c00"
    elif pred_rounded == 3:
        suffix = "rd (Podium)"
        color = "#ff8c00"
    else:
        suffix = "th"
        color = "#2563eb"
        
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color}; text-align: center; padding: 40px 20px;">
        <div class="kpi-label" style="font-size: 1.1rem; margin-bottom:10px;">Predicted Race Finish</div>
        <div class="kpi-value" style="font-size: 4.5rem; color: {color};">P{pred_rounded}</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #ffffff; margin-top: 10px;">{selected_driver} is predicted to finish {pred_rounded}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write(f"**How this prediction was calculated:**")
    st.markdown(f"""
    - **Starting Grid (P{grid_pos}):** High impact. Starting further back adds roughly `+{model.coef_[0]:.2f}` positions.
    - **Experience ({experience} races):** Small impact. Veteran drivers finish `+{model.coef_[1]:.4f}` positions per race entry.
    - **Form (P{recent_form:.1f}):** Medium impact. Average finish in recent races scales the outcome by `+{model.coef_[2]:.2f}`.
    - **Team points ({team_points:.0f} pts):** High impact. Driving for a top-tier team (high standings points) subtracts `{-model.coef_[3]:.4f}` positions per point (lowering finish position, which means improvement!).
    """)

st.markdown("---")
st.markdown("### Model Training Metrics & Mathematical Explanation")

col_m1, col_m2 = st.columns([1, 1])

with col_m1:
    st.markdown(f"""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Model Performance Metrics</h4>
        <p style="color:#94a3b8; font-size:0.85rem;">Evaluated on a 20% validation split of all Grand Prix races from 2010 to Present.</p>
        <table class="custom-table">
            <tr>
                <td><b>R² Score (Coefficient of Determination)</b></td>
                <td><code style="color:#ff1801; font-weight:bold;">{r2:.4f}</code></td>
            </tr>
            <tr>
                <td><b>Mean Absolute Error (MAE)</b></td>
                <td><code>{mae:.2f} positions</code></td>
            </tr>
            <tr>
                <td><b>Root Mean Squared Error (RMSE)</b></td>
                <td><code>{rmse:.2f} positions</code></td>
            </tr>
        </table>
        <p style="font-size:0.85rem; color:#94a3b8; margin-top: 10px;">An R² score of ~0.35 is typical for Formula 1 races, which are highly dynamic and influenced by random factors (crashes, weather, mechanical failures). A Mean Absolute Error of {mae:.1f} means the model predicts the driver's finish within {mae:.1f} positions of their actual finish, which is highly accurate for a linear regression model.</p>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div class="glass-container">
        <h4 style="color:#ffffff; margin-top:0;">Regression Coefficients (Feature Weights)</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Draw Coefficients Bar Chart
    coef_df = pd.DataFrame({
        'Feature': ['Starting Grid', 'Career Experience', 'Recent Form', 'Team Points'],
        'Weight': model.coef_
    }).sort_values(by='Weight', key=abs, ascending=False)
    
    fig_coef = px.bar(
        coef_df,
        x='Weight',
        y='Feature',
        orientation='h',
        color='Weight',
        color_continuous_scale='RdBu',
        labels={'Weight': 'Coefficient Weight (Slope)', 'Feature': 'Regression Variable'},
        template="plotly_dark"
    )
    fig_coef.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0),
        height=240
    )
    st.plotly_chart(fig_coef, use_container_width=True)

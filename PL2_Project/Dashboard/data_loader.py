import os
import pandas as pd
import numpy as np
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data')

def get_file_path(filename):
    return os.path.join(DATA_DIR, filename)

@st.cache_data
def load_csv(filename, replace_nulls=True):
    """Loads a CSV file and replaces '\\N' with standard NaN."""
    filepath = get_file_path(filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    # Read CSV
    df = pd.read_csv(filepath)
    
    # Replace Ergast's '\N' with NaN
    if replace_nulls:
        df = df.replace(r'\\N', np.nan, regex=True)
        df = df.replace(r'\\N', np.nan) # Handle non-string exact matches
        
    return df

@st.cache_data
def get_drivers():
    """Loads and cleans driver data."""
    df = load_csv('drivers.csv')
    df['driver_name'] = df['forename'] + ' ' + df['surname']
    # Clean up any potential types
    df['driverId'] = pd.to_numeric(df['driverId'])
    return df

@st.cache_data
def get_constructors():
    """Loads and cleans constructor data."""
    df = load_csv('constructors.csv')
    df['constructorId'] = pd.to_numeric(df['constructorId'])
    df = df.rename(columns={'name': 'constructor_name'})
    return df

@st.cache_data
def get_races():
    """Loads and cleans races data."""
    df = load_csv('races.csv')
    df['raceId'] = pd.to_numeric(df['raceId'])
    df['year'] = pd.to_numeric(df['year'])
    df['round'] = pd.to_numeric(df['round'])
    df['circuitId'] = pd.to_numeric(df['circuitId'])
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(by=['year', 'round'])
    return df

@st.cache_data
def get_circuits():
    """Loads and cleans circuits data."""
    df = load_csv('circuits.csv')
    df['circuitId'] = pd.to_numeric(df['circuitId'])
    return df

@st.cache_data
def get_results_merged():
    """Loads results and merges with races, drivers, and constructors."""
    results = load_csv('results.csv')
    races = get_races()
    drivers = get_drivers()
    constructors = get_constructors()
    
    # Clean numeric columns in results
    numeric_cols = ['resultId', 'raceId', 'driverId', 'constructorId', 'grid', 'positionOrder', 'points', 'laps', 'milliseconds', 'rank']
    for col in numeric_cols:
        if col in results.columns:
            results[col] = pd.to_numeric(results[col], errors='coerce')
            
    # Position can contain NaN (DNF), so we clean it but keep as numeric where possible
    results['position'] = pd.to_numeric(results['position'], errors='coerce')
    
    # Merge
    df = results.merge(races[['raceId', 'year', 'round', 'name', 'circuitId', 'date']], on='raceId', how='left')
    df = df.rename(columns={'name': 'race_name'})
    
    df = df.merge(drivers[['driverId', 'driverRef', 'driver_name', 'code', 'nationality', 'dob']], on='driverId', how='left')
    df = df.rename(columns={'nationality': 'driver_nationality'})
    
    df = df.merge(constructors[['constructorId', 'constructorRef', 'constructor_name', 'nationality']], on='constructorId', how='left')
    df = df.rename(columns={'nationality': 'constructor_nationality'})
    
    # Calculate positions gained/lost
    df['positions_gained'] = df['grid'] - df['positionOrder']
    
    return df

@st.cache_data
def get_driver_standings_merged():
    """Loads driver standings and merges with races and drivers."""
    standings = load_csv('driver_standings.csv')
    races = get_races()
    drivers = get_drivers()
    
    # Numeric conversions
    standings['driverStandingsId'] = pd.to_numeric(standings['driverStandingsId'])
    standings['raceId'] = pd.to_numeric(standings['raceId'])
    standings['driverId'] = pd.to_numeric(standings['driverId'])
    standings['points'] = pd.to_numeric(standings['points'])
    standings['position'] = pd.to_numeric(standings['position'])
    standings['wins'] = pd.to_numeric(standings['wins'])
    
    # Merge
    df = standings.merge(races[['raceId', 'year', 'round', 'name']], on='raceId', how='left')
    df = df.rename(columns={'name': 'race_name'})
    df = df.merge(drivers[['driverId', 'driver_name', 'code']], on='driverId', how='left')
    
    return df

@st.cache_data
def get_constructor_standings_merged():
    """Loads constructor standings and merges with races and constructors."""
    standings = load_csv('constructor_standings.csv')
    races = get_races()
    constructors = get_constructors()
    
    # Numeric conversions
    standings['constructorStandingsId'] = pd.to_numeric(standings['constructorStandingsId'])
    standings['raceId'] = pd.to_numeric(standings['raceId'])
    standings['constructorId'] = pd.to_numeric(standings['constructorId'])
    standings['points'] = pd.to_numeric(standings['points'])
    standings['position'] = pd.to_numeric(standings['position'])
    standings['wins'] = pd.to_numeric(standings['wins'])
    
    # Merge
    df = standings.merge(races[['raceId', 'year', 'round', 'name']], on='raceId', how='left')
    df = df.rename(columns={'name': 'race_name'})
    df = df.merge(constructors[['constructorId', 'constructor_name', 'constructorRef']], on='constructorId', how='left')
    
    return df

@st.cache_data
def get_qualifying_merged():
    """Loads qualifying and merges with races, drivers, constructors."""
    qualifying = load_csv('qualifying.csv')
    races = get_races()
    drivers = get_drivers()
    constructors = get_constructors()
    
    # Numeric conversions
    qualifying['qualifyId'] = pd.to_numeric(qualifying['qualifyId'])
    qualifying['raceId'] = pd.to_numeric(qualifying['raceId'])
    qualifying['driverId'] = pd.to_numeric(qualifying['driverId'])
    qualifying['constructorId'] = pd.to_numeric(qualifying['constructorId'])
    qualifying['position'] = pd.to_numeric(qualifying['position'])
    
    # Merge
    df = qualifying.merge(races[['raceId', 'year', 'round', 'name']], on='raceId', how='left')
    df = df.rename(columns={'name': 'race_name'})
    df = df.merge(drivers[['driverId', 'driver_name', 'code']], on='driverId', how='left')
    df = df.merge(constructors[['constructorId', 'constructor_name']], on='constructorId', how='left')
    
    return df

@st.cache_data
def get_pit_stops_merged():
    """Loads pit stops and merges with races and drivers."""
    pit_stops = load_csv('pit_stops.csv')
    races = get_races()
    drivers = get_drivers()
    
    # Numeric conversions
    pit_stops['raceId'] = pd.to_numeric(pit_stops['raceId'])
    pit_stops['driverId'] = pd.to_numeric(pit_stops['driverId'])
    pit_stops['stop'] = pd.to_numeric(pit_stops['stop'])
    pit_stops['lap'] = pd.to_numeric(pit_stops['lap'])
    pit_stops['milliseconds'] = pd.to_numeric(pit_stops['milliseconds'])
    
    # Convert duration to numeric, replace non-numeric values
    pit_stops['duration'] = pd.to_numeric(pit_stops['duration'], errors='coerce')
    
    # Merge
    df = pit_stops.merge(races[['raceId', 'year', 'round', 'name']], on='raceId', how='left')
    df = df.rename(columns={'name': 'race_name'})
    df = df.merge(drivers[['driverId', 'driver_name', 'code']], on='driverId', how='left')
    
    return df

@st.cache_data
def get_lap_times_for_race(race_id):
    """Loads and filters lap times for a specific race to save memory/time."""
    filepath = get_file_path('lap_times.csv')
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    # Read in chunks or use pandas query on filtered index to be faster
    # Since lap_times is 17MB, we can load it, but we can filter it
    # standard read is fine and fast enough with cache
    df = pd.read_csv(filepath)
    df = df[df['raceId'] == int(race_id)].copy()
    
    # Clean up
    df['raceId'] = pd.to_numeric(df['raceId'])
    df['driverId'] = pd.to_numeric(df['driverId'])
    df['lap'] = pd.to_numeric(df['lap'])
    df['position'] = pd.to_numeric(df['position'])
    df['milliseconds'] = pd.to_numeric(df['milliseconds'])
    
    # Merge driver name
    drivers = get_drivers()
    df = df.merge(drivers[['driverId', 'driver_name', 'code']], on='driverId', how='left')
    
    df = df.sort_values(by=['lap', 'position'])
    return df

@st.cache_data
def get_driver_summary():
    """Loads the pre-computed driver summary dataset."""
    df = load_csv('driver_summary.csv')
    return df

@st.cache_data
def get_constructor_summary():
    """Loads the pre-computed constructor summary dataset."""
    df = load_csv('constructor_summary.csv')
    return df

@st.cache_data
def get_status_mapping():
    """Loads status codes mapping."""
    df = load_csv('status.csv')
    df['statusId'] = pd.to_numeric(df['statusId'])
    return df

import sys
import os

# Ensure the Dashboard folder is in the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Dashboard'))

try:
    print("Testing data loader imports...")
    import data_loader as dl
    
    print("Loading drivers...")
    drivers = dl.get_drivers()
    print(f"Loaded {len(drivers)} drivers successfully.")
    
    print("Loading constructors...")
    constructors = dl.get_constructors()
    print(f"Loaded {len(constructors)} constructors successfully.")
    
    print("Loading races...")
    races = dl.get_races()
    print(f"Loaded {len(races)} races successfully.")
    
    print("Loading merged results...")
    results = dl.get_results_merged()
    print(f"Loaded {len(results)} merged results rows successfully.")
    
    print("Testing Linear Regression model training on F1 dataset...")
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    
    # Simple feature prep test
    results = results.sort_values(by=['year', 'round', 'positionOrder']).copy()
    results['driver_experience'] = results.groupby('driverId').cumcount()
    results['driver_form'] = results.groupby('driverId')['positionOrder'].shift(1).rolling(3, min_periods=1).mean().fillna(results['grid'])
    
    # standings prev points test
    standings = dl.load_csv('driver_standings.csv')
    standings['points'] = pd = sys.modules['pandas'].to_numeric(standings['points'])
    standings['raceId'] = sys.modules['pandas'].to_numeric(standings['raceId'])
    standings['driverId'] = sys.modules['pandas'].to_numeric(standings['driverId'])
    standings['prev_points'] = standings.groupby('driverId')['points'].shift(1).fillna(0)
    
    merged = results.merge(standings[['raceId', 'driverId', 'prev_points']], on=['raceId', 'driverId'], how='left')
    merged['prev_points'] = merged['prev_points'].fillna(0)
    
    model_df = merged[merged['year'] >= 2010].dropna(subset=['positionOrder', 'grid', 'driver_experience', 'driver_form', 'prev_points'])
    features = ['grid', 'driver_experience', 'driver_form', 'prev_points']
    
    X = model_df[features]
    y = model_df['positionOrder']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    print("Model trained successfully!")
    print(f"Feature coefficients: {model.coef_}")
    print(f"Model intercept: {model.intercept_}")
    print("ALL TESTS PASSED SUCCESSFULLY! Data loader and Scikit-Learn logic are operational.")
    
except Exception as e:
    print(f"TEST FAILED! Error details: {e}")
    sys.exit(1)

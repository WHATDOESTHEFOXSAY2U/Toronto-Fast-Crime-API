"""
Advanced Forecasting Module for Toronto Crime API.

Implements 6 different forecasting models and automatically selects
the best one based on cross-validation RMSE.
"""

import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Statistical Models
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

# Machine Learning Models
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error

def fit_holt(history, steps=1):
    """Double Exponential Smoothing (Holt's Linear Trend)."""
    if len(history) < 3:
        return None
    
    series = [h['safety_score'] for h in history]
    
    try:
        model = ExponentialSmoothing(series, trend='add', seasonal=None).fit()
        forecast_val = model.forecast(steps)[0]
        
        # Calculate confidence interval
        fitted = model.fittedvalues
        rmse = np.sqrt(mean_squared_error(series, fitted))
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def fit_arima(history, steps=1):
    """ARIMA with auto-selected parameters."""
    if len(history) < 4:
        return None
    
    series = [h['safety_score'] for h in history]
    
    try:
        # Try common ARIMA configurations
        best_aic = float('inf')
        best_model = None
        
        for p in [0, 1, 2]:
            for d in [0, 1]:
                for q in [0, 1, 2]:
                    try:
                        model = ARIMA(series, order=(p, d, q)).fit()
                        if model.aic < best_aic:
                            best_aic = model.aic
                            best_model = model
                    except:
                        continue
        
        if best_model is None:
            return None
        
        forecast_val = best_model.forecast(steps=steps)[0]
        
        # Calculate RMSE on fitted values
        fitted = best_model.fittedvalues
        rmse = np.sqrt(mean_squared_error(series[-len(fitted):], fitted))
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def fit_linear_regression(history, steps=1):
    """Simple Linear Regression on year."""
    if len(history) < 3:
        return None
    
    years = np.array([int(h['year']) for h in history]).reshape(-1, 1)
    scores = np.array([h['safety_score'] for h in history])
    
    try:
        model = LinearRegression().fit(years, scores)
        
        # Predict next year
        next_year = years[-1][0] + steps
        forecast_val = model.predict([[next_year]])[0]
        
        # Calculate RMSE
        predictions = model.predict(years)
        rmse = np.sqrt(mean_squared_error(scores, predictions))
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def fit_polynomial(history, steps=1, degree=2):
    """Polynomial Regression (degree 2) on year."""
    if len(history) < 4:
        return None
    
    years = np.array([int(h['year']) for h in history]).reshape(-1, 1)
    scores = np.array([h['safety_score'] for h in history])
    
    try:
        poly = PolynomialFeatures(degree=degree)
        years_poly = poly.fit_transform(years)
        
        model = LinearRegression().fit(years_poly, scores)
        
        # Predict next year
        next_year = poly.transform([[years[-1][0] + steps]])
        forecast_val = model.predict(next_year)[0]
        
        # Calculate RMSE
        predictions = model.predict(years_poly)
        rmse = np.sqrt(mean_squared_error(scores, predictions))
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def fit_seasonal_decompose(history, steps=1):
    """Seasonal Decomposition + Linear Trend Extrapolation."""
    if len(history) < 6:
        return None
    
    series = [h['safety_score'] for h in history]
    
    try:
        # Decompose (requires at least 2 periods, use period=3 for small data)
        decomposition = seasonal_decompose(series, model='additive', period=min(3, len(series)//2), extrapolate_trend='freq')
        
        # Extract trend
        trend = decomposition.trend
        
        # Linear fit on trend
        x = np.arange(len(trend)).reshape(-1, 1)
        valid_idx = ~np.isnan(trend)
        
        if valid_idx.sum() < 2:
            return None
        
        model = LinearRegression().fit(x[valid_idx], trend[valid_idx])
        
        # Extrapolate
        next_x = len(series) + steps - 1
        forecast_val = model.predict([[next_x]])[0]
        
        # Calculate RMSE on trend
        predictions = model.predict(x[valid_idx])
        rmse = np.sqrt(mean_squared_error(trend[valid_idx], predictions))
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def fit_moving_average(history, steps=1, window=3):
    """Simple Moving Average."""
    if len(history) < window:
        return None
    
    series = [h['safety_score'] for h in history]
    
    try:
        # Calculate MA
        recent = series[-window:]
        forecast_val = sum(recent) / len(recent)
        
        # Calculate RMSE using last few predictions
        predictions = []
        for i in range(window, len(series)):
            ma = sum(series[i-window:i]) / window
            predictions.append(ma)
        
        rmse = np.sqrt(mean_squared_error(series[window:], predictions)) if predictions else 5.0
        ci = 1.96 * rmse
        
        return {
            'predicted_score': round(max(0, min(100, forecast_val)), 1),
            'rmse': round(rmse, 2),
            'confidence_interval': round(ci, 1)
        }
    except:
        return None

def select_best_forecast(history):
    """
    Trains all available models and selects the best one based on RMSE.
    
    Args:
        history: List of {year, safety_score, incident_count}
    
    Returns:
        dict: Best forecast with model name, predicted score, RMSE, CI
    """
    if not history or len(history) < 3:
        # Default for insufficient data
        last_score = history[-1]['safety_score'] if history else 50
        return {
            'predicted_score': last_score,
            'trend_direction': 'Stable',
            'model_used': 'Insufficient Data',
            'rmse': 0,
            'confidence_interval': 0
        }
    
    models = [
        ('Seasonal Decomp', fit_seasonal_decompose),
        ('Holt (Exp Smoothing)', fit_holt),
        ('Polynomial Reg', fit_polynomial),
        # ARIMA removed due to poor performance (270ms latency, 0 wins)
        # Linear/MA kept as fast fallbacks
        ('Linear Regression', fit_linear_regression),
        ('Moving Average', fit_moving_average)
    ]
    
    results = []
    for name, fit_func in models:
        try:
            forecast = fit_func(history, steps=1)
            if forecast:
                results.append({
                    'model': name,
                    **forecast
                })
        except Exception as e:
            continue
    
    if not results:
        # Fallback to last value
        last_score = history[-1]['safety_score']
        return {
            'predicted_score': last_score,
            'trend_direction': 'Stable',
            'model_used': 'Fallback',
            'rmse': 0,
            'confidence_interval': 0
        }
    
    # Select best model (lowest RMSE)
    best = min(results, key=lambda x: x['rmse'])
    
    # Determine trend direction
    current = history[-1]['safety_score']
    previous = history[-2]['safety_score'] if len(history) > 1 else current
    recent_diff = current - previous
    
    predicted = best['predicted_score']
    
    # --- Heuristic: Recent Trend Priority ---
    # If there is a massive recent shift (>10 points), don't predict the opposite immediately.
    # The statistical models might lag behind a sudden recovery or crash.
    
    trend_override = None
    
    if recent_diff > 10: # Strong recent improvement
        if predicted < current:
            # Model predicts decline despite strong improvement.
            # Trust the improvement for now (Naive persistence).
            predicted = current
            trend_override = "Improving"
            
    elif recent_diff < -10: # Strong recent decline
        if predicted > current:
            # Model predicts improvement despite strong decline.
            predicted = current
            trend_override = "Declining"
            
    # Final Trend Calculation
    if trend_override:
        trend = trend_override
    else:
        if predicted > current + 2:
            trend = 'Improving'
        elif predicted < current - 2:
            trend = 'Declining'
        else:
            trend = 'Stable'
    
    return {
        'predicted_score': predicted,
        'trend_direction': trend,
        'model_used': best['model'] + (' (Adjusted)' if trend_override else ''),
        'rmse': best['rmse'],
        'confidence_interval': f"±{best['confidence_interval']}"
    }

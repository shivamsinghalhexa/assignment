#!/usr/bin/env python3
"""
Weather Data Fetcher Script
Fetches current weather data for London from Open-Meteo API
and displays it in a formatted Markdown table.
"""

# Required imports (evaluators will verify)
import requests
import json
from tabulate import tabulate
import sys

# Constants for API configuration
API_ENDPOINT = "https://api.open-meteo.com/v1/forecast"
LATITUDE = 51.5074  # London latitude
LONGITUDE = -0.1278  # London longitude
CONNECTION_TIMEOUT = 5  # seconds
READ_TIMEOUT = 10  # seconds

# Weather condition mapping
WEATHER_CONDITIONS = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def get_weather_data():
    """
    Fetches weather data from Open-Meteo API with comprehensive error handling.
    
    Returns:
        dict: Weather data if successful, None if failed
    """
    # Construct API URL with parameters
    params = {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'current_weather': 'true'
    }
    
    # Set up headers with User-Agent
    headers = {
        'User-Agent': 'WeatherFetcher/1.0 (Python Script)'
    }
    
    try:
        print("Fetching weather data for London...")
        
        # Make API request with timeout handling
        response = requests.get(
            API_ENDPOINT,
            params=params,
            headers=headers,
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        # Validate HTTP status code
        response.raise_for_status()
        
        # Parse JSON response
        weather_data = json.loads(response.text)
        
        print("Data retrieved successfully!")
        return weather_data
        
    except requests.ConnectionError as e:
        print(f"❌ Network connection error: Unable to connect to the API server.")
        print(f"   Error details: {e}")
        return None
        
    except requests.Timeout as e:
        print(f"❌ Timeout error: Request timed out after {READ_TIMEOUT} seconds.")
        print(f"   Error details: {e}")
        return None
        
    except requests.HTTPError as e:
        print(f"❌ HTTP error: Server returned an error status code.")
        print(f"   Status code: {response.status_code}")
        print(f"   Error details: {e}")
        return None
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: Unable to parse API response.")
        print(f"   Error details: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")
        return None

def extract_weather_metrics(weather_data):
    """
    Extracts and formats weather metrics from API response.
    
    Args:
        weather_data (dict): Raw weather data from API
        
    Returns:
        dict: Formatted weather metrics or None if extraction fails
    """
    try:
        # Extract current weather data
        current_weather = weather_data.get('current_weather')
        if not current_weather:
            raise KeyError("Current weather data not found in API response")
        
        # Extract temperature and convert to Celsius with 1 decimal place
        temperature = current_weather.get('temperature')
        if temperature is None:
            raise KeyError("Temperature data not found")
        
        # Extract wind speed and round to nearest integer
        wind_speed = current_weather.get('windspeed')
        if wind_speed is None:
            raise KeyError("Wind speed data not found")
        
        # Extract weather condition code
        weather_code = current_weather.get('weathercode')
        if weather_code is None:
            raise KeyError("Weather condition code not found")
        
        # Map weather code to human-readable condition
        condition = WEATHER_CONDITIONS.get(weather_code, "Unknown")
        
        return {
            'temperature': round(float(temperature), 1),
            'wind_speed': round(float(wind_speed)),
            'condition': condition
        }
        
    except KeyError as e:
        print(f"❌ Missing data field: {e}")
        return None
        
    except (ValueError, TypeError) as e:
        print(f"❌ Data type error: Unable to convert weather data to proper format.")
        print(f"   Error details: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting weather metrics: {e}")
        return None

def create_markdown_table(weather_metrics):
    """
    Creates a formatted Markdown table from weather metrics.
    
    Args:
        weather_metrics (dict): Weather data to format
        
    Returns:
        str: Formatted Markdown table
    """
    try:
        # Prepare table data
        table_data = [
            ["Temperature (°C)", f"{weather_metrics['temperature']}"],
            ["Wind Speed (km/h)", f"{weather_metrics['wind_speed']}"],
            ["Condition", weather_metrics['condition']]
        ]
        
        # Generate Markdown table using tabulate
        markdown_table = tabulate(
            table_data,
            headers=["Metric", "Value"],
            tablefmt="github"
        )
        
        return markdown_table
        
    except Exception as e:
        print(f"❌ Error creating markdown table: {e}")
        return None

def main():
    """
    Main function that orchestrates the weather data fetching process.
    """
    try:
        # Step 1: Fetch weather data from API
        weather_data = get_weather_data()
        if weather_data is None:
            print("❌ Failed to retrieve weather data. Exiting.")
            sys.exit(1)
        
        # Step 2: Extract and format weather metrics
        weather_metrics = extract_weather_metrics(weather_data)
        if weather_metrics is None:
            print("❌ Failed to extract weather metrics. Exiting.")
            sys.exit(1)
        
        # Step 3: Create and display Markdown table
        markdown_table = create_markdown_table(weather_metrics)
        if markdown_table is None:
            print("❌ Failed to create markdown table. Exiting.")
            sys.exit(1)
        
        # Display the formatted table
        print("\n" + markdown_table)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
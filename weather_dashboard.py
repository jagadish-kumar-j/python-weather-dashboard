"""
╔══════════════════════════════════════════════════════════════════╗
║         PYTHON WEATHER DASHBOARD                                 ║
║         Using OpenWeatherMap API                                 ║
║         Language  : Python 3.x                                   ║
║         Library   : requests                                     ║
║         API       : OpenWeatherMap (api.openweathermap.org)      ║
╚══════════════════════════════════════════════════════════════════╝

Project   : Real-Time Weather Dashboard
Purpose   : Fetch and display live weather data for any city
Author    : [Your Name]
College   : [Your College Name]
Dept      : Computer Science and Business Systems
Batch     : 2027
"""

# ─────────────────────────────────────────────
# IMPORTING REQUIRED LIBRARIES
# ─────────────────────────────────────────────
import builtins
import os
import requests   # For making HTTP API calls
import sys        # For system-level exit on critical errors


def safe_print(*args, sep=" ", end="\n", file=sys.stdout, flush=False):
    """Print text safely, replacing characters that cannot be encoded by the terminal."""
    try:
        builtins.print(*args, sep=sep, end=end, file=file, flush=flush)
    except UnicodeEncodeError:
        text = sep.join(str(arg) for arg in args)
        encoding = getattr(file, "encoding", None) or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(encoding)
        builtins.print(safe_text, end=end, file=file, flush=flush)


print = safe_print


# ─────────────────────────────────────────────
# GLOBAL CONFIGURATION
# ─────────────────────────────────────────────
DEFAULT_API_KEY = ""   # Replace this with your own key if needed
API_KEY = os.environ.get("OPENWEATHER_API_KEY", DEFAULT_API_KEY)
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"  # API endpoint


# ══════════════════════════════════════════════
# FUNCTION 1: kelvin_to_celsius(temp)
# PURPOSE   : Converts temperature from Kelvin to Celsius
# INPUT     : temp (float) — temperature in Kelvin
# OUTPUT    : temperature (float) in Celsius, rounded to 1 decimal
# FORMULA   : °C = K − 273.15
# ══════════════════════════════════════════════
def kelvin_to_celsius(temp):
    """
    Converts Kelvin temperature to Celsius.

    OpenWeatherMap API returns temperatures in Kelvin by default.
    This function subtracts 273.15 from the Kelvin value.

    Args:
        temp (float): Temperature in Kelvin.

    Returns:
        float: Temperature in Celsius, rounded to 1 decimal place.
    """
    celsius = temp - 273.15          # Standard Kelvin to Celsius formula
    return round(celsius, 1)         # Round to 1 decimal for clean display


# ══════════════════════════════════════════════
# FUNCTION 2: get_feel(temp)
# PURPOSE   : Returns a comfort label based on temperature
# INPUT     : temp (float) — temperature in Celsius
# OUTPUT    : comfort label string (Cold / Pleasant / Warm / Hot)
# LOGIC     : Uses predefined temperature thresholds
# ══════════════════════════════════════════════
def get_feel(temp):
    """
    Returns a human-readable comfort label based on Celsius temperature.

    Comfort Scale:
        Below 15°C  → Cold
        15 – 25°C   → Pleasant
        25 – 32°C   → Warm
        Above 32°C  → Hot

    Args:
        temp (float): Temperature in Celsius.

    Returns:
        str: Comfort label string.
    """
    if temp < 15:
        return "❄️  Cold"
    elif 15 <= temp <= 25:
        return "😊 Pleasant"
    elif 25 < temp <= 32:
        return "☀️  Warm"
    else:
        return "🔥 Hot"


# ══════════════════════════════════════════════
# FUNCTION 3: get_weather(city, api_key)
# PURPOSE   : Fetches real-time weather data from OpenWeatherMap API
# INPUT     : city (str) — city name entered by user
#             api_key (str) — valid OpenWeatherMap API key
# OUTPUT    : dict with weather data fields, OR None on failure
# HANDLES   : Invalid city, invalid key, no internet, timeout
# ══════════════════════════════════════════════
def get_weather(city, api_key):
    """
    Fetches current weather data for the given city using the OpenWeatherMap API.

    Sends an HTTP GET request to the weather endpoint with the city name
    and API key as query parameters. Returns parsed weather data or None.

    Args:
        city    (str): Name of the city to look up.
        api_key (str): Valid OpenWeatherMap API key.

    Returns:
        dict: Parsed weather data with keys:
              city, country, description, temp_c, feels_like_c, humidity, wind_speed
        None: If any error occurred (error message is printed internally).

    Raises:
        Handled internally — function prints descriptive error messages.
    """

    # Build query parameters for the API request
    params = {
        "q"       : city,       # City name (e.g., "Chennai")
        "appid"   : api_key,    # API authentication key
    }

    try:
        # ── Send HTTP GET Request ──────────────────────────────────────
        # timeout=10 prevents the program from hanging forever if server is slow
        response = requests.get(BASE_URL, params=params, timeout=10)

        # ── HTTP 200 → Success ─────────────────────────────────────────
        if response.status_code == 200:
            data = response.json()   # Parse JSON response into Python dict

            # Extract and structure the fields we need
            weather_data = {
                "city"        : data["name"],                          # City name from API
                "country"     : data["sys"]["country"],                # Country code (IN, US, etc.)
                "description" : data["weather"][0]["description"].title(),  # e.g., "Partly Cloudy"
                "temp_k"      : data["main"]["temp"],                  # Temp in Kelvin
                "feels_like_k": data["main"]["feels_like"],            # Feels-like in Kelvin
                "humidity"    : data["main"]["humidity"],              # Humidity in %
                "wind_speed"  : data["wind"]["speed"],                 # Wind speed in m/s
            }

            # Convert Kelvin to Celsius using our custom function
            weather_data["temp_c"]       = kelvin_to_celsius(weather_data["temp_k"])
            weather_data["feels_like_c"] = kelvin_to_celsius(weather_data["feels_like_k"])

            return weather_data   # Return the complete dictionary

        # ── HTTP 404 → City Not Found ──────────────────────────────────
        elif response.status_code == 404:
            print(f"\n  ❌ ERROR: City '{city}' not found.")
            print("     Please check the spelling and try again.\n")
            return None

        # ── HTTP 401 → Invalid API Key ─────────────────────────────────
        elif response.status_code == 401:
            print("\n  ❌ ERROR: Invalid API Key.")
            print("     Please verify your OpenWeatherMap API key.\n")
            return None

        # ── Other HTTP Errors ──────────────────────────────────────────
        else:
            print(f"\n  ❌ ERROR: Unexpected response from server.")
            print(f"     HTTP Status Code: {response.status_code}\n")
            return None

    # ── No Internet / DNS Failure ──────────────────────────────────────
    except requests.exceptions.ConnectionError:
        print("\n  ❌ ERROR: No internet connection.")
        print("     Please check your network and try again.\n")
        return None

    # ── Request Timed Out ──────────────────────────────────────────────
    except requests.exceptions.Timeout:
        print("\n  ❌ ERROR: Request timed out.")
        print("     The server took too long to respond. Try again later.\n")
        return None

    # ── Other Unexpected Exceptions ────────────────────────────────────
    except requests.exceptions.RequestException as e:
        print(f"\n  ❌ ERROR: An unexpected error occurred.\n  Details: {e}\n")
        return None


# ══════════════════════════════════════════════
# FUNCTION 4: display_dashboard(data)
# PURPOSE   : Displays weather data in a formatted dashboard
# INPUT     : data (dict) — weather data returned by get_weather()
# OUTPUT    : Printed dashboard to console
# ══════════════════════════════════════════════
def display_dashboard(data):
    """
    Displays the weather information in a clean, professional dashboard format.

    Extracts all values from the data dictionary, computes comfort status,
    and prints a neatly bordered dashboard to the terminal.

    Args:
        data (dict): Weather data dictionary from get_weather().
    """

    # ── Extract values from dictionary ────────────────────────────────
    city        = data["city"]
    country     = data["country"]
    description = data["description"]
    temp_c      = data["temp_c"]
    feels_like  = data["feels_like_c"]
    humidity    = data["humidity"]
    wind_speed  = data["wind_speed"]

    # ── Compute comfort status via get_feel() ─────────────────────────
    comfort     = get_feel(temp_c)

    # ── Choose weather icon based on description keywords ─────────────
    desc_lower  = description.lower()
    if "clear" in desc_lower:
        icon = "☀️ "
    elif "cloud" in desc_lower:
        icon = "🌤 "
    elif "rain" in desc_lower:
        icon = "🌧 "
    elif "storm" in desc_lower or "thunder" in desc_lower:
        icon = "⛈ "
    elif "snow" in desc_lower:
        icon = "❄️ "
    elif "mist" in desc_lower or "fog" in desc_lower or "haze" in desc_lower:
        icon = "🌫 "
    else:
        icon = "🌡 "

    # ── Build dynamic header width ────────────────────────────────────
    title       = f" WEATHER DASHBOARD — {city.upper()}, {country} "
    width       = max(len(title) + 2, 42)   # Minimum width of 42
    border_top  = "╔" + "═" * width + "╗"
    border_bot  = "╚" + "═" * width + "╝"
    title_line  = "║" + title.center(width) + "║"

    # ── Print the Dashboard ────────────────────────────────────────────
    print()
    print(border_top)
    print(title_line)
    print(border_bot)
    print()
    print(f"  {icon}  Weather     : {description}")
    print(f"  🌡  Temperature : {temp_c}°C  ({comfort})")
    print(f"  🥵  Feels Like  : {feels_like}°C")
    print(f"  💧  Humidity    : {humidity}%")
    print(f"  🍃  Wind Speed  : {wind_speed} m/s")
    print()
    print("  ─────────────────────────────────────────")
    print(f"  📍  Location    : {city}, {country}")
    print("  🔄  Source      : OpenWeatherMap API (Live)")
    print("  ─────────────────────────────────────────")
    print()


# ══════════════════════════════════════════════
# MAIN PROGRAM ENTRY POINT
# PURPOSE   : Controls program flow — input → fetch → display
# ══════════════════════════════════════════════
def main():
    """
    Main function that drives the Weather Dashboard program.

    Steps:
        1. Print welcome banner
        2. Ask user for a city name
        3. Validate input (not empty)
        4. Call get_weather() to fetch data
        5. Call display_dashboard() to show results
        6. Ask user if they want to check another city
    """

    # ── Welcome Banner ─────────────────────────────────────────────────
    print()
    print("  ╔════════════════════════════════════════╗")
    print("  ║    🌍  PYTHON WEATHER DASHBOARD  🌍    ║")
    print("  ║    Powered by OpenWeatherMap API       ║")
    print("  ╚════════════════════════════════════════╝")
    print()

    # ── Main Loop — allows checking multiple cities ────────────────────
    while True:

        # Step 1: Get city input from user
        city = input("  Enter city name (or 'quit' to exit): ").strip()

        # Step 2: Handle empty input
        if not city:
            print("  ⚠️  No city name entered. Please try again.\n")
            continue

        # Step 3: Handle quit command
        if city.lower() in ["quit", "exit", "q"]:
            print("\n  👋  Thank you for using Weather Dashboard. Goodbye!\n")
            break

        # Step 4: Check API key configuration
        if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
            print("\n  ❌ ERROR: OpenWeatherMap API key is not configured.")
            print("     Set the OPENWEATHER_API_KEY environment variable or update DEFAULT_API_KEY.")
            print("     https://openweathermap.org/appid\n")
            break

        # Step 5: Fetch weather data
        print(f"\n  🔄  Fetching weather data for '{city}'...")
        weather_data = get_weather(city, API_KEY)

        # Step 6: Display dashboard if data was retrieved successfully
        if weather_data:
            display_dashboard(weather_data)

        # Step 6: Ask if user wants to check another city
        again = input("  Check another city? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n  👋  Thank you for using Weather Dashboard. Goodbye!\n")
            break
        print()


# ─────────────────────────────────────────────
# PROGRAM EXECUTION GUARD
# Ensures main() is only called when the script
# is run directly, not when imported as a module
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()

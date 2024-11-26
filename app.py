from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)  # Session will expire after 30 minutes

API_KEY = "177d82b9bad36d7e0e1dc0214f2a808a"

def fetch_weather(city, unit):
    """Helper function to fetch weather data from OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("cod") == 200:
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"]
            }
        else:
            return {"error": data.get("message", "City not found.")}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error_message = None
    favorites = session.get("favorites", [])

    if request.method == "POST":
        city = request.form.get("city")
        unit = request.form.get("unit", "metric")

        if city:
            result = fetch_weather(city, unit)

            if "error" in result:
                error_message = result["error"]
            else:
                weather_data = result

                # Add to favorites if requested
                if request.form.get("add_favorite"):
                    if city not in favorites:
                        favorites.append(city)
                        session["favorites"] = favorites
        else:
            error_message = "Please enter a city name."

    return render_template("index.html", weather=weather_data, error=error_message, favorites=favorites)

@app.route("/remove_favorite/<city>")
def remove_favorite(city):
    favorites = session.get("favorites", [])
    if city in favorites:
        favorites.remove(city)
        session["favorites"] = favorites
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

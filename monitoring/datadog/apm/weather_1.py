from flask import Flask, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import json
from urllib.request import urlopen
from urllib.error import URLError
from typing import dict, Optional
from dataclasses import dataclass
from datetime import datetime

app = Flask(__name__)

# Setting path for database file
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "weather.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Weather(db.Model):
    """Weather data model"""
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(5), nullable=False)
    coordinate = db.Column(db.String(20), nullable=False)
    temp = db.Column(db.String(5))
    pressure = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    cityname = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


with app.app_context():
    db.create_all()


def kelvin_to_celsius(temp: float) -> str:
    """Convert temperature from Kelvin to Celsius"""
    return str(round(float(temp) - 273.16, 2))


def get_default_city() -> str:
    """Get default city name"""
    return 'Delhi'


def save_to_database(weather_details: dict) -> None:
    """Save weather details to database"""
    weather = Weather(
        country_code=weather_details["country_code"],
        coordinate=weather_details["coordinate"],
        temp=weather_details["temp"],
        pressure=int(weather_details["pressure"]),
        humidity=int(weather_details["humidity"]),
        cityname=weather_details["cityname"]
    )
    db.session.add(weather)
    db.session.commit()


def get_weather_details(city: str) -> Optional[dict]:
    """Fetch weather details from OpenWeatherMap API"""
    api_key = os.getenv('OPENWEATHER_API_KEY', '48a90ac42c53')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    
    try:
        with urlopen(url) as response:
            source = response.read()
    except (URLError, Exception) as e:
        print(f"Error fetching weather data: {e}")
        abort(400)
    
    # Converting JSON data to dictionary
    list_of_data = json.loads(source)
    
    # Extract and structure weather data
    data = {
        "country_code": list_of_data['sys']['country'],
        "coordinate": f"{list_of_data['coord']['lon']} {list_of_data['coord']['lat']}",
        "temp": f"{list_of_data['main']['temp']}k",
        "temp_cel": f"{kelvin_to_celsius(list_of_data['main']['temp'])}C",
        "pressure": list_of_data['main']['pressure'],
        "humidity": list_of_data['main']['humidity'],
        "cityname": city,
    }
    
    save_to_database(data)
    return data


@app.route('/', methods=['GET', 'POST'])
def weather():
    """Handle weather requests"""
    city = request.form.get('city') if request.method == 'POST' else get_default_city()
    data = get_weather_details(city)
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
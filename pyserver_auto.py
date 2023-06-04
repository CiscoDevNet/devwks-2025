from flask import Flask, render_template, request, redirect, jsonify
import os
import requests
from statistics import mean 

app = Flask(__name__)

@app.route('/weather-auto', methods=('GET', 'POST'))
def index():
    """
    Flask function to render index.html page + form
    """

    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        temp = get_temperature(latitude=latitude,longitude=longitude)
        messages = { "temp" : temp }

        return render_template('index_auto.html', messages=messages)

    return render_template('index_auto.html')

@app.route("/checkweather")
def checkweather():
    """
    Flask server side function to request the temperature from get_temperature function
    """
    latitude = request.args['latitude']
    longitude = request.args['longitude']
    temperature = get_temperature(latitude,longitude)
    return jsonify(temperature)


def get_temperature(latitude,longitude):
    """
    weather request via open-meteo APIs with longitude + latitude
    """
    try:
        r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m")
        r_data = r.json()
        temperatures = r_data["hourly"]["temperature_2m"]
        temp_of_day = temperatures[:24]
        average_temp = mean(temp_of_day)
        r_string = average_temp
        return r_string
    except Exception as e:
        r_string = f"Error: {e}"
        return r_string

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)

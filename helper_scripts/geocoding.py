
import requests

def get_lat_long(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': place_name,
        'key': ''
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    else:
        return "Coordinates not found", "Coordinates not found"

print(get_lat_long("Van Gogh's studio, Paris, France"))


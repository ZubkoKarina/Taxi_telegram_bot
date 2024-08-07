import googlemaps
from data.config import API_KEY_GOOGLE_MAP
import requests

gmaps = googlemaps.Client(key=API_KEY_GOOGLE_MAP)


async def find_region(region: str):
    place_result = gmaps.places_autocomplete(region, components={"country": "ua"}, language='uk')
    if place_result:
        place_id = place_result[0]['place_id']
        place_details = gmaps.place(place_id, language='uk')
        print(place_details)
        if place_details and 'address_components' in place_details['result']:
            for component in place_details['result']['address_components']:
                if 'administrative_area_level_1' in component['types']:
                    return component['long_name']


async def find_city(city: str, region: str):
    place_result = gmaps.places(f'{city}, {region}', location="ua", language='uk')
    if place_result:
        return place_result['results'][0]['name']


def find_places_by_name(place: str, location: set):
    place_result = gmaps.geocode(f'{place}', language='uk')
    if place_result:
        print(place_result)
        for place in place_result[0]['address_components']:
            if 'street_number' in place['types']:
                print(f'Street Number: {place["long_name"]}')
            if 'route' in place['types']:
                print(f"Street Name: {place['long_name']}")
            if 'locality' in place['types']:
                print(f"City: {place['long_name']}")


find_places_by_name('просект Відродження 28, Луцьк, Волинська область, Україна, 43000', (0, 0))
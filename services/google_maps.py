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
    place_result = gmaps.geocode(f'{city}, {region}, Україна', language='uk')
    if place_result:

        for place in place_result[0]['address_components']:
            if 'locality' in place['types']:
                return place['long_name']


async def geocode_place_by_name(place: str):
    geocode_place = {}
    place_result = gmaps.geocode(f'{place}', language='uk')
    if place_result:
        geocode_place['place_id'] = place_result[0]['place_id']
        geocode_place['location'] = place_result[0]['geometry']['location']
        for place in place_result[0]['address_components']:
            if 'street_number' in place['types']:
                geocode_place['house'] = place["long_name"]
            if 'route' in place['types']:
                geocode_place['street'] = place['long_name']
            if 'locality' in place['types']:
                geocode_place['city'] = place['long_name']
            if 'administrative_area_level_1' in place['types']:
                geocode_place['region'] = place['long_name']
        return geocode_place
    else:
        return None


async def geocode_place_by_geo(geo: set):
    result = gmaps.reverse_geocode(geo)
    if result:
        return {"place": result['formatted_address'], "place_id": result['place_id']}
    else:
        return None
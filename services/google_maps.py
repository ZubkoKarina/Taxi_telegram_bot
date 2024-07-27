import googlemaps
from data.config import API_KEY_GOOGLE_MAP

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



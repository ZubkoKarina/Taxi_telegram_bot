import requests
from data.config import API_KEY_VISICOM, API_URL_VISICOM_DATA
import json


def get_place(query: str = None, place_id: str = None, categories: str = None):
    url = API_URL_VISICOM_DATA + "/geocode"

    params = {
        'text': query,
        'key': API_KEY_VISICOM,
        'limit': 1,
        'near': place_id,
        'country': 'ua',
        'categories': categories
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)
        properties = data.get('properties')
        geo = data.get('geo_centroid').get('coordinates')
        address = {
            'house': properties.get('name'),
            'street': f'{properties.get("street_type")} {properties.get("street")}',
            'city': properties.get('settlement')
        }
        print({'id': data.get('id'), 'geo': {'lat': geo[1], 'lng': geo[0]}, 'address': address, 'region_id': properties.get('level3_id')})
        return {'id': data.get('id'), 'geo': {'lat': geo[1], 'lng': geo[0]}, 'address': address, 'region_id': properties.get('level3_id', data.get('id'))}
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def autocomplete(query, near_place_id: str = None, intersect_place_id: str = None,
                 categories_exclude: str = None, categories: str = None):
    url = API_URL_VISICOM_DATA + "/geocode"

    params = {
        'text': query,
        'key': API_KEY_VISICOM,
        'country': 'ua',
        'near': near_place_id,
        'intersect': intersect_place_id,
        'limit': 15,
        'categories_exclude': categories_exclude,
        "categories": categories
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('features') is None:
            return [data]
        return data.get('features')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_address_numbers(place_id: str, geometry: str = 'no'):
    url = f'{API_URL_VISICOM_DATA}/feature/{place_id}.json'

    params = {
        'key': API_KEY_VISICOM,
        'geometry': geometry,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        address_list = []
        for item in data.get('properties').get('address', []):
            address_name = data.get('properties').get('name')
            address_number = item.get('name')
            address_type = data.get('properties').get('type')

            address_list.append({
                'name': f"{address_type} {address_name} {address_number}",
                'address': f"{address_type} {address_name} {address_number}, {data.get('properties').get('settlement')}",
                'id': item.get('id'),
                'description': data.get('properties').get('settlement'),
            })

        return address_list
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_place_geo(place_id: str, geometry: str = 'no'):
    url = f'{API_URL_VISICOM_DATA}/feature/{place_id}.json'

    params = {
        'key': API_KEY_VISICOM,
        'geometry': geometry,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(f'INFO: place geo -> {data}')
        return data.get('geo_centroid').get('coordinates')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def visicom_address_constructor(feature_collection):
    feature_collection_formatted = []
    if feature_collection is None or feature_collection == []:
        return None
    for item in feature_collection:
        properties = item.get('properties')
        if 'adm_settlement' in properties.get('categories'):
            print(properties)
            address_dict = {
                'name': f"{properties.get('type')} {properties.get('name')}",
                'description': properties.get('level1'),
                'address': f"{properties.get('name')}, {properties.get('level1')}",
                'id': item.get('id'),
                'categories': properties.get('categories'),
                'geo': [item.get('geo_centroid').get('coordinates')[1], item.get('geo_centroid').get('coordinates')[0]]
            }
            feature_collection_formatted.append(address_dict)

        if 'poi' in properties.get('categories'):
            address_dict = {
                'name': f"{properties.get('name')}, {properties.get('address')}",
                'description': properties.get('address'),
                'address':  f"{properties.get('name')}, {properties.get('address')}",
                'id': item.get('id'),
                'categories': properties.get('categories')
            }
            feature_collection_formatted.append(address_dict)

        elif 'adr_street' in properties.get('categories'):
            address_dict = {
                'name': f"{properties.get('type')} {properties.get('name')}",
                'description': properties.get('settlement'),
                'address': f"{properties.get('type')} {properties.get('name')}, {properties.get('settlement')}",
                'id': item.get('id'),
                'categories': properties.get('categories')
            }
            feature_collection_formatted.append(address_dict)

        elif 'adr_address' in properties.get('categories'):
            address_dict = {
                'name': f"{properties.get('street_type')} {properties.get('street')} {properties.get('name')}",
                'description': properties.get('settlement'),
                'address': f"{properties.get('street_type')} {properties.get('street')} {properties.get('name')}, {properties.get('settlement')}",
                'id': item.get('id'),
                'categories': properties.get('categories')
            }
            feature_collection_formatted.append(address_dict)
    return feature_collection_formatted


def get_place_by_geo(lat, lng):
    url = API_URL_VISICOM_DATA + "/geocode"
    print(f'{lat}, {lng}')

    params = {
        'key': API_KEY_VISICOM,
        'limit': 1,
        'country': 'ua',
        'near': f'{lng},{lat}',
        'radius': 100,
        'categories': 'adr_street,adr_address',
        'categories_exclude': 'adm_country,adm_district,adm_level1,adm_place,adm_settlement,hst_district,roa_road,adm_level2,adm_level3'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if len(data) != 0:
            address_dict = visicom_address_constructor([data])

            return address_dict[0]
        else:
            return {
                'name': f"Місцезнаходження <br>{round(lat, 6)}, {round(lng, 6)}",
                'description': '',
                'address': f"{lat}, {lng}",
                'id': '',
                'categories': 'geo'
            }
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def search_settlement(city: str, region: str):
    url = API_URL_VISICOM_DATA + "/geocode"
    region_id = get_place(region).get('id')

    params = {
        'text': city,
        'key': API_KEY_VISICOM,
        'intersect': region_id,
        'limit': 5,
        'country': 'ua',
        'categories': 'adm_settlement'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data == {}:
            return None
        print(data)
        if data.get('features') is not None and data.get('features')[0].get('properties').get('class') != 'city':
            return 'DUPLICATE'
        if data.get('features') is None:
            properties = data.get('properties')
        else:
            properties = data.get('features')[0].get('properties')
        if properties.get('class') == 'village':
            return f'{properties.get("name")} ({properties.get("level2")})'
        return properties.get("name")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


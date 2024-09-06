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
        print({'id': data.get('id'), 'geo': {'lat': geo[1], 'lng': geo[0]}, 'address': address})
        return {'id': data.get('id'), 'geo': {'lat': geo[1], 'lng': geo[0]}, 'address': address}
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
        'limit': 25,
        'categories_exclude': categories_exclude,
        "categories": categories
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
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

        return data.get('geo_centroid').get('coordinates')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def visicom_address_constructor(feature_collection):

    feature_collection_formatted = []
    for item in feature_collection:
        properties = item.get('properties')

        if 'poi' in properties.get('categories'):
            address_dict = {
                'name': f"{properties.get('name')}",
                'description': properties.get('address'),
                'address': properties.get('address'),
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
        'radius': 100,
        'near': f'{lng},{lat}',
        'categories': 'adr_address'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        properties = data.get('properties')

        address_dict = {
            'name': f"{properties.get('street_type')} {properties.get('street')} {properties.get('name')},  {properties.get('settlement')}",
            'description': properties.get('settlement'),
            'address': f"{properties.get('street_type')} {properties.get('street')} {properties.get('name')}, {properties.get('settlement')}",
            'id': data.get('id'),
            'categories': properties.get('categories')
        }
        print(address_dict)
        return address_dict
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# categories_exclude = 'adm_country,adm_district,adm_level1,adm_place,adm_settlement,hst_district,roa_road'
# res = autocomplete(query='Шкільна 5', near_place_id='STL1NYCM9',
#              categories_exclude='adm_country,adm_district,adm_level1,adm_place,adm_settlement,hst_district,roa_road')
# address = visicom_address_constructor(res)
# for i in address:
#     print(i.get('name'), i.get('description'))

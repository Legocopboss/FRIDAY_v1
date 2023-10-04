import os

import requests
from typing import Dict, Any


url = 'http://api.mediastack.com/v1/news'
api_key = str(os.getenv("NEWS_API_KEY"))
weather_api_key = str(os.getenv("WEATHER_API_KEY"))

def get_current_event(keywords=None, categories="general"):
    resp = requests.get(
        url=url,
        params={
            'access_key': api_key,
            'keywords': keywords,
            'categories': categories,
            'languages': 'en',
            'countries': 'us',
            'sort': 'published_desc',
            'limit': '10',
        }
    )

    return(str(resp.json()))


def accuweather_api_request(config: Dict[str, Any]):
    # You can use the 'requests' library to make HTTP requests

    # Extract the necessary parameters from the config
    endpoint = config.get('endpoint')
    method = config.get('method')
    queryParams = config.get('queryParams')
    body = config.get('body')

    # Make the API request
    url = f"https://api.accuweather.com/{endpoint}"
    headers = {
        'apikey': weather_api_key
    }
    params = queryParams if queryParams else {}
    data = body if body else {}

    if method == 'GET':
        response = requests.get(url, params=params, headers=headers)
    elif method == 'POST':
        response = requests.post(url, params=params, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, params=params, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, params=params, headers=headers, json=data)
    else:
        return {'error': 'Invalid method'}

    # Extract and return the response JSON
    return str(response.json())
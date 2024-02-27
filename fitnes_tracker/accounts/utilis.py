import requests
import os
class Edamam(object):
    def __init__(self):
        self.app_id = os.environ.get('API_id')
        self.app_key = os.environ.get('API_key')

    def get_food_data(self, food_name):
        api_endpoint = "https://api.edamam.com/auto-complete"
        payload = {
            "ingr": food_name,
            "app_id": self.app_id,
            "app_key": self.app_key,
        }
        response = requests.get(api_endpoint, params=payload)
        return response.json()
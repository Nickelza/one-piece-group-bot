import random

import requests

import resources.Environment as Env
from src.model.game.whoswho.Character import Character


class SupabaseRest:
    def __init__(self):
        """
        Creates a wiki object
        """
        self.rest_url = Env.SUPABASE_REST_URL.get()
        self.api_key = Env.SUPABASE_API_KEY.get()

    def make_get_request(self, path):
        """
        Make a request to the Supabase REST API
        :param path: The path to the resource
        :return: The response
        """

        full_path = f'{self.rest_url}{path}'
        # Make request
        response = requests.get(
            url=full_path,
            headers={
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
        )

        # Check response
        if response.status_code != 200:
            raise Exception(f'Error making request to {full_path}')

        # Return response
        return response.json()

    @staticmethod
    def get_random_character() -> Character:
        """
        Get a random character
        :return: A random character
        """

        # Get a random character
        response: list[dict] = SupabaseRest().make_get_request('character')

        # Randomly select a character
        character_dict = random.choice(response)

        # Return character
        return Character(**character_dict)

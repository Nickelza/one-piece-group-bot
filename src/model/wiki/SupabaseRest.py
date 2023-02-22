import random

import requests

import resources.Environment as Env
from src.model.error.CustomException import WikiException
from src.model.wiki.Character import Character
from src.model.wiki.Terminology import Terminology


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

        if len(response) == 0:
            raise WikiException('No characters found')

        # Randomly select a character
        character_dict = random.choice(response)

        # Return character
        return Character(**character_dict)

    @staticmethod
    def get_random_terminology(max_len: int = None, only_letters: bool = False,
                               consider_len_without_space: bool = False, allow_spaces: bool = True) -> Terminology:
        """
        Get a random terminology
        :param max_len: The maximum length of the terminology
        :param only_letters: Whether the terminology should only contain letters
        :param consider_len_without_space: Whether the length of the terminology should be considered without spaces
        :param allow_spaces: Whether the terminology can contain spaces if only_letters is True
        :return: A random terminology
        """

        # Get a random terminology
        response: list[dict] = SupabaseRest().make_get_request('terminology')
        response_filtered = response.copy()

        if max_len is not None or only_letters:
            for term in response:
                if max_len is not None and len(term['name']) > max_len:
                    if not (consider_len_without_space and len(str(term['name']).replace(' ', '')) <= max_len):
                        response_filtered.remove(term)
                        continue

                if only_letters and not str(term['name']).isalpha():
                    if not (allow_spaces and str(term['name']).replace(' ', '').isalpha()):
                        response_filtered.remove(term)
                        continue

                if not consider_len_without_space and ' ' in term['name']:
                    response_filtered.remove(term)
                    continue

        if len(response_filtered) == 0:
            raise WikiException('No terminologies found')

        # Randomly select a terminology
        terminology_dict = random.choice(response_filtered)

        # Return terminology
        return Terminology(**terminology_dict)

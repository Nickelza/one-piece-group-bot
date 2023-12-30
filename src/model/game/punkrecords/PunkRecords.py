import json
import random

import resources.Environment as Env
from src.model.wiki.Character import Character

REVEALABLE_DETAILS = ["Affiliations", "Occupations", "Residence", "Status"]


class RevealedDetail:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class PunkRecords:
    def __init__(
        self, character: Character, revealed_details: dict = None, revealed_letters_count: int = 0
    ):
        """
        Constructor

        :param character: The character
        :param revealed_details: The revealed details, a dictionary with the key being the name of the revealed detail
                                and the value being the indexes of the values that have been revealed
        :param revealed_letters_count: The revealed letters count
        """
        self.character = character
        self.revealed_details = {} if revealed_details is None else revealed_details
        self.revealed_letters_count = revealed_letters_count

        # No details revealed, reveal the first n
        if len(self.revealed_details) == 0:
            for i in range(Env.PUNK_RECORDS_STARTING_DETAILS.get_int()):
                try:
                    new_detail = self.get_random_detail_to_reveal()
                    self.set_revealed_detail(new_detail)
                except ValueError:  # No more details to reveal
                    break

    def get_board_json(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, separators=(",", ":")
        )

    def is_correct(self, answer: str) -> bool:
        """
        Check if the answer is correct
        :param answer: The answer
        :return: bool
        """
        return answer is not None and answer.lower() == self.character.name.lower()

    def have_revealed_all_letters(self) -> bool:
        """
        Check if all letters have been revealed
        :return: bool
        """
        return self.revealed_letters_count == len(self.character.name)

    def can_reveal_detail(self) -> bool:
        """
        Check if there is any detail that can be revealed
        :return: bool
        """

        for name in REVEALABLE_DETAILS:
            if name in self.character.info_box["Statistics"] and not self.detail_is_revealed(name):
                return True

    def detail_is_revealed(self, name: str) -> bool:
        """
        Check if the detail is revealed
        :param name: The name of the detail
        :return: bool
        """

        if name not in self.revealed_details:
            return False

        if isinstance(self.character.info_box["Statistics"][name], str):
            return True

        return len(self.revealed_details[name]) == len(self.character.info_box["Statistics"][name])

    def get_random_detail_to_reveal(self) -> RevealedDetail:
        """
        Get the detail to reveal
        :return: The detail to reveal
        """

        def get_detail(_name: str):
            # If detail is string, return it
            if isinstance(self.character.info_box["Statistics"][_name], str):
                return RevealedDetail(_name, self.character.info_box["Statistics"][_name])

            # If detail is list, return a random value that has not already been revealed
            indexes_to_pick_from = [
                i
                for i in range(len(self.character.info_box["Statistics"][_name]))
                if i not in self.revealed_details[_name]
            ]

            return RevealedDetail(
                _name,
                self.character.info_box["Statistics"][_name][random.choice(indexes_to_pick_from)],
            )

        # First, iterate all revealable details. If a new key is found, return a random value of it
        for name in REVEALABLE_DETAILS:
            if name in self.character.info_box["Statistics"] and not self.detail_is_revealed(name):
                if name not in self.revealed_details:
                    self.revealed_details[name] = []
                    return get_detail(name)

        # No new key, get a detail that has been only revealed partially
        # Create a list of tuples to store the name , the amount of revealed values and the total amount of values
        tuples_list: list[tuple[str, int, int]] = []
        for name in REVEALABLE_DETAILS:
            if name in self.character.info_box["Statistics"]:
                # If a string, amount of revealed values is 1 and total amount of values is 1
                if isinstance(self.character.info_box["Statistics"][name], str):
                    tuples_list.append((name, 1, 1))
                else:
                    # If a list, amount of revealed values is the length of the revealed values and total amount of
                    # values is the length of the list
                    tuples_list.append((
                        name,
                        len(self.revealed_details[name]),
                        len(self.character.info_box["Statistics"][name]),
                    ))

        # Sort the list by the amount of revealed values
        tuples_list.sort(key=lambda x: x[1])

        # Get the first element without all values revealed
        for name, revealed_values, total_values in tuples_list:
            if revealed_values < total_values:
                return get_detail(name)

        raise ValueError("No detail to reveal")

    def get_revealed_detail(self, name) -> str | list:
        """
        Get the detail
        :param name: The name of the detail
        :return: The detail
        """

        if isinstance(self.character.info_box["Statistics"][name], str):
            return self.character.info_box["Statistics"][name]

        return [
            self.character.info_box["Statistics"][name][i] for i in self.revealed_details[name]
        ]

    def set_revealed_detail(self, detail: RevealedDetail) -> None:
        """
        Set the revealed detail
        :param detail: The detail
        :return: None
        """
        # If is string, add list of index 0
        if isinstance(self.get_revealed_detail(detail.name), str):
            self.revealed_details[detail.name] = [0]
        else:
            # List, add index of revealed value
            self.revealed_details[detail.name].append(
                self.character.info_box["Statistics"][detail.name].index(detail.value)
            )

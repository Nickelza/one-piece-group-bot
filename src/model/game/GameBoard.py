import json


class GameBoard:
    def __init__(self):
        pass

    def get_as_json_string(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, separators=(",", ":")
        )

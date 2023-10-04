import json

from src.model.pojo.Keyboard import Keyboard


class ContextDataValue:
    def __init__(self, title: str, text: any, args: tuple = None, description: str = None,
                 keyboard: list[list[Keyboard]] = None):
        self.title = title
        self.text = text
        self.args = args
        self.description = description
        self.keyboard = keyboard

    def get_json(self) -> str:
        """Get the json representation of the object"""
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))

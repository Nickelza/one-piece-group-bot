import json
from enum import StrEnum


class IncomeTaxReductionType(StrEnum):
    ADMIN = 'admin'
    CREW_ability = 'crew_ability'
    DEVIL_FRUIT = 'devil_fruit'


class IncomeTaxReduction:
    def __init__(self, reduction_type: IncomeTaxReductionType, amount: float):
        self.reduction_type = reduction_type
        self.amount = amount

    def get_json(self) -> str:
        """
        Get the JSON representation
        :return: The JSON representation
        """

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))

    @staticmethod
    def from_string(reduction_list: str) -> list['IncomeTaxReduction']:
        """
        Get the tax reduction list from a string
        :param reduction_list: The string
        :return: The tax reduction list
        """
        if not reduction_list:
            return []

        reduction_list_json = json.loads(reduction_list)
        return [IncomeTaxReduction(**reduction) for reduction in reduction_list_json]

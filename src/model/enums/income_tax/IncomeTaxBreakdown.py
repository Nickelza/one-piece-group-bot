import json


class IncomeTaxBreakdown:
    def __init__(self, taxable_amount: int, percentage: float, tax_amount: int):
        self.taxable_amount = taxable_amount
        self.tax_percentage = percentage
        self.tax_amount = tax_amount

    def get_json(self) -> str:
        """
        Get the JSON representation
        :return: The JSON representation
        """

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))

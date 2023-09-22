from src.service.message_service import escape_valid_markdown_chars


class Terminology:
    # noinspection PyUnusedLocal
    # **kwargs is used to ignore unused arguments
    def __init__(self, name: str, info_url: str, **kwargs):
        """Initialize the character."""
        self.name = name
        self.info_url = info_url

    def get_markdown_mention(self) -> str:
        """
        Returns the markdown mention of the character
        :return: The markdown mention of the character
        """

        return f'[{escape_valid_markdown_chars(self.name)}]({escape_valid_markdown_chars(self.info_url)})'

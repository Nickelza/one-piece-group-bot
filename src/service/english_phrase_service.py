from resources import phrases


def determine_article(word) -> str:
    """
    Determines the article for the given word.

    :param word: The word to get the article for
    :return: The article for the given word
    """
    if word[0].lower() in ["a", "e", "i", "o", "u"]:
        return "an"
    return "a"


def get_word_with_article(word) -> str:
    """
    Returns the word with the correct article

    :param word: The word to get the article for
    :return: The word with the article
    """

    return f"{determine_article(word)} {word}"


def day_or_days(count: int) -> str:
    """
    Returns the correct word for day or days

    :param count: The count
    :return: The correct word for day or days
    """
    return phrases.TEXT_DAY if count == 1 else phrases.TEXT_DAYS

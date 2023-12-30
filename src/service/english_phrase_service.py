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

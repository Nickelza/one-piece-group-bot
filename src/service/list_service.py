import resources.phrases as phrases
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard


def get_navigation_buttons(inbound_keyboard: Keyboard, current_page: int) -> list[Keyboard]:
    """
    Returns the navigation buttons for the crew member list
    :param inbound_keyboard: The inbound keyboard
    :param current_page: The current page
    :return: The navigation buttons
    """

    keyboard_line: list[Keyboard] = []

    # Previous page
    previous_page_button_info = {ReservedKeyboardKeys.PAGE: current_page - 1}
    keyboard_line.append(Keyboard(phrases.PVT_KEY_PREVIOUS_PAGE, info=previous_page_button_info,
                                  inbound_info=inbound_keyboard.info))

    # Next page
    next_page_button_info = {ReservedKeyboardKeys.PAGE: current_page + 1}
    keyboard_line.append(Keyboard(phrases.PVT_KEY_NEXT_PAGE, info=next_page_button_info,
                                  inbound_info=inbound_keyboard.info))

    return keyboard_line

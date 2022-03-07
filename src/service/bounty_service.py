from PIL import Image, ImageFont, ImageDraw
from telegram import Update
from unidecode import unidecode

import constants as c
import resources.Environment as Env
from src.model.User import User
from src.service.download_service import generate_temp_file_path
from src.service.user_service import get_user_profile_photo


def get_bounty_formatted(bounty: int) -> str:
    """
    Returns a formatted string of the bounty
    :param bounty: The bounty to format e.g. 1000000
    :return: The formatted string e.g. 1,000,000
    """

    return '{0:,}'.format(bounty)


def get_message_belly(update: Update) -> int:
    """
    Calculates how much bellys a message is worth
    :param update: Telegram update
    :return: How much bellys a message is worth
    """

    # Command message - No belly
    try:
        if update.message.text[0] in c.COMMAND_PREFIX_ALIASES:
            return 0
    except (AttributeError, TypeError):
        pass

    # Callback query - No belly
    try:
        if update.callback_query.data is not None:
            return 0
    except AttributeError:
        pass

    # Forwarded message - Base belly
    try:
        if update.message.forward_from is not None:
            return int(Env.BELLY_BASE_MESSAGE.get())
    except AttributeError:
        pass

    final_belly: float = int(Env.BELLY_BASE_MESSAGE.get())

    # Char multiplier - Text messages which are not forwarded
    try:
        char_belly = (1 + (len(update.message.text) * float(Env.BELLY_CHARACTER_MULTIPLIER.get())))
        # Cap if it exceeds the max allowed per character count
        max_char_belly = float(Env.BELLY_CHARACTER_MAX_MULTIPLE.get()) * float(Env.BELLY_BASE_MESSAGE.get())
        char_belly = char_belly if char_belly <= max_char_belly else max_char_belly
        final_belly += char_belly
    except (AttributeError, TypeError):
        pass

    # Reply to channel post multiplier
    try:
        if update.message.reply_to_message.sender_chat.id == int(Env.OPD_CHANNEL_ID.get()):
            final_belly *= float(Env.BELLY_REPLY_TO_CHANNEL_POST_MULTIPLIER.get())
    except AttributeError:
        pass

    # Sticker multiplier
    try:
        if update.message.sticker is not None:
            final_belly *= float(Env.BELLY_STICKER_MULTIPLIER.get())
    except AttributeError:
        pass
    # Animation multiplier
    try:
        if update.message.animation is not None:
            final_belly *= float(Env.BELLY_ANIMATION_MULTIPLIER.get())
    except AttributeError:
        pass

    return round(int(final_belly), -3)  # Round to the nearest thousandth


def get_poster_name(user: User) -> str:
    """
    Gets the bounty poster's name of a user
    :param user: The user to get the poster's name of
    :return: The name to display on the bounty poster
    """

    # Set values
    first_name = user.tg_first_name if user.tg_first_name is not None else ''
    last_name = user.tg_last_name if user.tg_last_name is not None else ''

    # Normalize to ascii
    first_name = unidecode(first_name).upper().strip()
    last_name = unidecode(last_name).upper().strip()

    # Get full name
    full_name = (first_name + ' ' + last_name).strip()

    while True:  # Should run only once
        if len(full_name) <= c.POSTER_NAME_MAX_LENGTH:
            break

        # Use first name only
        full_name = first_name
        if len(full_name) <= c.POSTER_NAME_MAX_LENGTH:
            break

        # Still too long, split by 'space' and concatenate till it's not too long
        parts = full_name.split(' ')
        result = ''
        for part in parts:
            if len(result + ' ' + part) > c.POSTER_NAME_MAX_LENGTH:
                break
            result += ' ' + part

        # Use result or only the first part
        full_name = parts[0] if len(result) == 0 else result
        if len(full_name) <= c.POSTER_NAME_MAX_LENGTH:
            break

        # Still too long, remove extra characters
        full_name = full_name[:(c.POSTER_NAME_MAX_LENGTH - 2)] + '.'
        break

    # Add space sub if too long or D. in name
    if len(full_name) >= c.POSTER_NAME_SPACE_SUB_MIN_LENGTH or 'D.' in full_name:
        full_name = full_name.replace(' ', c.POSTER_NAME_SPACE_SUB_CHAR)

    # Replace 'D.' with 'D'
    full_name = full_name.replace('D.', 'D')

    return full_name


def get_poster_component(text: str, c_type: int) -> Image:
    """
    Get a component of the poster
    :param text: Text to be written
    :param c_type: Type of component (1 - name, 2 - berry)
    :return: Component image
    """

    if c_type == c.POSTER_COMPONENT_NAME:  # Name component
        texture_path = c.POSTER_NAME_TEXTURE_PATH
        font_path = c.POSTER_NAME_FONT_PATH
        font_size = c.POSTER_NAME_FONT_SIZE
        max_w = c.POSTER_NAME_MAX_W
        max_kern = c.POSTER_NAME_MAX_KERN
        x_pos = c.POSTER_NAME_START_X
        box_h = c.POSTER_NAME_H

    elif c_type == c.POSTER_COMPONENT_BERRY:  # Berry component
        texture_path = c.POSTER_BERRY_TEXTURE_PATH
        font_path = c.POSTER_BERRY_FONT_PATH
        font_size = c.POSTER_BERRY_FONT_SIZE
        max_w = c.POSTER_BERRY_MAX_W
        max_kern = c.POSTER_BERRY_MAX_KERN
        x_pos = c.POSTER_BERRY_START_X
        box_h = c.POSTER_BERRY_H
    else:
        raise Exception('Invalid component type')

    texture_background: Image = Image.open(texture_path)
    texture_background_w, texture_background_h = texture_background.size
    font: ImageFont = ImageFont.truetype(font_path, font_size)

    # Create new alpha channel - solid black
    # Alpha with more height to account for characters that are cut off under
    alpha: Image = Image.new('L', (texture_background_w, texture_background_h))
    draw: ImageDraw = ImageDraw.Draw(alpha)

    # Get text size
    should_scale: bool = False
    text_w, text_h = draw.textsize(text, font=font)

    if text_w < max_w:
        width_difference = max_w - text_w
        kern = int(width_difference / (len(text) - 1))

        # Avoid too much kerning
        if kern > max_kern:
            kern = max_kern
            x_pos += int((max_w / 2) - ((text_w + (kern * (len(text) - 1))) / 2))

        # Draw char by char considering kerning
        for char in text:
            draw.text((x_pos, box_h), char, font=font, fill='white', anchor='ls')
            char_width, letter_height = draw.textsize(char, font=font)
            x_pos += char_width + kern
    else:
        # If width is too big, increase alpha channel width
        if text_w > max_w:
            # Calculate new width
            new_w = int((text_w * texture_background_w) / max_w)
            alpha = Image.new('L', (new_w, texture_background_h))
            draw = ImageDraw.Draw(alpha)
            should_scale = True

        # Draw text on baseline in the image
        draw.text((int(alpha.size[0] / 2), box_h), text, font=font, fill='white', anchor='ms')

        # Scale texture image if needed
        if should_scale:
            alpha = alpha.resize((texture_background_w, texture_background_h))

    # Use text cutout as alpha channel for texture image
    texture_background.putalpha(alpha)

    return texture_background


def get_poster(update: Update, user: User) -> str:
    """
    Gets the bounty poster of a user
    :param update: Telegram update
    :param user: The user to get the poster of
    :return: The poster of the bounty
    """

    # Open poster template
    poster_template = Image.open(c.POSTER_TEMPLATE_PATH).convert("RGBA")
    # Get poster template size
    poster_template_width, poster_template_height = poster_template.size

    # Create a new image with the same size as the template
    new_image = Image.new("RGB", poster_template.size)

    # Get profile photo of user
    profile_photo_path = get_user_profile_photo(update)
    if profile_photo_path is None:
        profile_photo_path = c.POSTER_NO_PHOTO_PATH

    # Add profile photo
    profile_photo = Image.open(profile_photo_path)
    # Get profile photo size
    profile_photo_width, profile_photo_height = profile_photo.size
    # Get delta between profile image height and image box height
    delta = profile_photo_height - c.POSTER_IMAGE_BOX_H
    # Get where profile image should be placed
    profile_photo_y = c.POSTER_IMAGE_BOX_START_Y - int(delta / 2)
    # Profile photo should be placed in the center of the poster template
    profile_photo_x = int((poster_template_width - profile_photo_width) / 2)
    # Paste profile image into the new image
    new_image.paste(profile_photo, (profile_photo_x, profile_photo_y))

    # Paste poster template into the new image
    new_image.paste(poster_template, (0, 0), mask=poster_template)

    # Add name component
    full_name = get_poster_name(user)
    name_component: Image = get_poster_component(full_name, c.POSTER_COMPONENT_NAME)
    new_image.paste(name_component, (0, c.POSTER_NAME_START_Y), name_component)

    # Add berry component
    berry = get_bounty_formatted(user.bounty) + '-'
    berry_component: Image = get_poster_component(berry, c.POSTER_COMPONENT_BERRY)
    new_image.paste(berry_component, (0, c.POSTER_BERRY_START_Y), berry_component)

    # Save image
    save_path = generate_temp_file_path(c.POSTER_EXTENSIION)
    new_image.save(save_path)

    return save_path

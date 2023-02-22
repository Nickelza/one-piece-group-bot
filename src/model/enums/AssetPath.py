import os
from enum import StrEnum

import constants as c


class AssetPath(StrEnum):
    """
    Class for assets path
    """

    # Saved Media
    CREW_INVITE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'crew_invite.jpg')
    CREW_JOIN = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'join_crew.jpg')
    DEVIL_FRUIT_NEW = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'devil_fruit_new.jpg')
    DOC_Q = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'docq.jpg')
    FIGHT = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'fight.jpg')
    GAME = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'game.jpg')
    GAME_ROCK_PAPER_SCISSORS = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'game_rock_paper_scissors.jpg')
    GAME_RUSSIAN_ROULETTE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'game_russian_roulette.jpg')
    GAME_SHAMBLES = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'shambles.jpg')
    GAME_WHOS_WHO = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'game_whos_who.jpg')
    SILENCE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, 'silence.jpg')

    # Other images
    GAME_BACKGROUND = os.path.join(c.ASSETS_IMAGES_DIR, 'game_background.jpg')

    # Fonts
    FONT_BLOGGER_SANS_BOLD = os.path.join(c.ASSETS_FONTS_DIR, 'Blogger_Sans-Bold.otf')

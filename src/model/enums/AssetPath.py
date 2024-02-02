import os
from enum import StrEnum

import constants as c


class AssetPath(StrEnum):
    """
    Class for assets path
    """

    # Saved Media
    CREW_INVITE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "crew_invite.jpg")
    CREW_JOIN = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "crew_join.jpg")
    DEVIL_FRUIT_NEW = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "devil_fruit_new.jpg")
    DOC_Q = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "docq.jpg")
    FIGHT = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "fight.jpg")
    GAME = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game.jpg")
    GAME_ROCK_PAPER_SCISSORS = os.path.join(
        c.ASSETS_SAVED_MEDIA_DIR, "game_rock_paper_scissors.jpg"
    )
    GAME_RUSSIAN_ROULETTE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game_russian_roulette.jpg")
    GAME_SHAMBLES = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game_shambles.jpg")
    GAME_WHOS_WHO = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game_whos_who.jpg")
    GAME_GUESS_OR_LIFE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game_guess_or_life.jpg")
    GAME_PUNK_RECORDS = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "game_punk_records.jpg")
    SILENCE = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "silence.jpg")
    PLUNDER = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "plunder.jpg")
    PLUNDER_SUCCESS = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "plunder_success.jpg")
    PLUNDER_FAIL = os.path.join(c.ASSETS_SAVED_MEDIA_DIR, "plunder_fail.jpg")

    # Other images
    GAME_BACKGROUND = os.path.join(c.ASSETS_IMAGES_DIR, "game_background.jpg")

    # Fonts
    FONT_BLOGGER_SANS_BOLD = os.path.join(c.ASSETS_FONTS_DIR, "Blogger_Sans-Bold.otf")

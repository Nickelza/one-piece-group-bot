import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.game.GameDifficulty import GameDifficulty
from src.model.game.GameType import GameType


class Game(BaseModel):
    """
    Game class
    """
    id = PrimaryKeyField()
    challenger = ForeignKeyField(User, backref='game_challengers', on_delete='CASCADE',
                                 on_update='CASCADE')
    opponent = ForeignKeyField(User, backref='game_opponents', on_delete='CASCADE', on_update='CASCADE', null=True)
    type = SmallIntegerField(null=True)
    board = CharField(max_length=9999, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.AWAITING_SELECTION)
    group_chat = ForeignKeyField(GroupChat, null=True, backref='game_groups_chats', on_delete='RESTRICT',
                                 on_update='CASCADE')
    message_id = IntegerField(null=True)
    wager = IntegerField(null=True)
    last_interaction_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'game'

    def is_player(self, user: User) -> bool:
        """
        Check if the user is a player of the game
        :param user: The user
        :return: True if the user is a player, False otherwise
        """

        return self.challenger == user or self.opponent == user

    def get_saved_media_name(self) -> SavedMediaName:
        """
        Get the SavedMediaName for this GameType
        :return: The SavedMediaName
        """
        return GameType(self.type).get_saved_media_name()

    def get_difficulty(self) -> GameDifficulty:
        """
        Get the difficulty level of the game
        :return: The difficulty level
        """

        return GameDifficulty.get_from_total_wager(int(str(self.wager)))

    def get_name(self) -> str:
        """
        Get the name of the game
        :return: The name
        """

        return GameType(self.type).get_name()

    @staticmethod
    def get_total_win_or_loss_or_draw(user: User, status: GameStatus) -> int:
        """
        Get the total amount of wins or losses or draws a user has
        param user: The user
        param status: The status (won or lost or draw)
        return: The total amount of wins or losses or draws
        """

        if status in (GameStatus.WON, GameStatus.LOST):
            return (Game().select().where((Game.challenger == user) & (Game.status == status)).count()
                    + Game().select().where((Game.opponent == user) & (Game.status == status.get_opposite_status()))
                    .count())

        return Game().select().where((Game.challenger == user) & (Game.status == status)).count()

    @staticmethod
    def get_total_belly_won_or_lost(user: User, status: GameStatus) -> int:
        """
        Get the total amount of belly a user has won or lost
        param user: The user
        param status: The status (won or lost)
        return: The total amount of belly
        """

        return (Game.select(fn.SUM(Game.wager)).where((Game.challenger == user)
                                                      & (Game.status == status))
                + (Game.select(fn.SUM(Game.wager)).where((Game.opponent == user)
                                                         & (Game.status == status.get_opposite_status())))).scalar()

    @staticmethod
    def get_max_won_or_lost(user: User, status: GameStatus) -> 'Game':
        """
        Get the game with the max belly won or lost
        param user: The user
        param status: The status (won or lost)
        return: The game
        """

        # Max game as challenger
        max_game_as_challenger: Game = (Game().select()
                                        .where((Game.challenger == user) & (Game.status == status))
                                        .order_by(Game.wager.desc())
                                        .first())

        # Max game as opponent
        max_game_as_opponent: Game = (Game().select()
                                      .where((Game.opponent == user) & (Game.status == status.get_opposite_status()))
                                      .order_by(Game.wager.desc())
                                      .first())

        if max_game_as_challenger is None:
            return max_game_as_opponent

        if max_game_as_opponent is None:
            return max_game_as_challenger

        if max_game_as_challenger.wager > max_game_as_opponent.wager:
            return max_game_as_challenger

        return max_game_as_opponent

    @staticmethod
    def get_most_challenged_user(user: User) -> (User, int):
        """
        Get the most challenged user and the amount of games
        param user: The user
        return: The most challenged user and the amount of games
        """

        # noinspection DuplicatedCode
        most_challenged_user_as_challenger = (Game.select(Game.opponent, fn.COUNT(Game.opponent).alias('count'))
                                              .where(Game.challenger == user)
                                              .group_by(Game.opponent)
                                              .order_by(SQL('count').desc())
                                              .first())
        amount_as_challenger = most_challenged_user_as_challenger.count

        most_challenged_user_as_opponent = (Game.select(Game.challenger, fn.COUNT(Game.challenger).alias('count'))
                                            .where(Game.opponent == user)
                                            .group_by(Game.challenger)
                                            .order_by(SQL('count').desc())
                                            .first())
        amount_as_opponent = most_challenged_user_as_opponent.count

        if amount_as_challenger > amount_as_opponent:
            return most_challenged_user_as_challenger.opponent, amount_as_challenger

        return most_challenged_user_as_opponent.challenger, amount_as_opponent

    @staticmethod
    def get_most_played_game(user: User) -> (GameType, int):
        """
        Get the most played game and the amount of games
        param user: The user
        return: The most played game and the amount of games
        """

        # noinspection DuplicatedCode
        most_played_as_challenger = (Game.select(Game.type, fn.COUNT(Game.type).alias('count'))
                                     .where(Game.challenger == user)
                                     .group_by(Game.type)
                                     .order_by(SQL('count').desc())
                                     .first())
        amount_as_challenger = most_played_as_challenger.count

        most_played_as_opponent = (Game.select(Game.type, fn.COUNT(Game.type).alias('count'))
                                   .where(Game.opponent == user)
                                   .group_by(Game.type)
                                   .order_by(SQL('count').desc())
                                   .first())
        amount_as_opponent = most_played_as_opponent.count

        if amount_as_challenger > amount_as_opponent:
            return GameType(most_played_as_challenger.type), amount_as_challenger

        return GameType(most_played_as_opponent.type), amount_as_opponent

    def get_type(self) -> GameType:
        """
        Get the GameType
        :return: The GameType
        """
        return GameType(self.type)


Game.create_table()

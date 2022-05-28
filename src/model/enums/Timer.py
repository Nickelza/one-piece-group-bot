import resources.Environment as Env


class Timer:
    """
    This class is used to create a timer
    """

    def __init__(self, name: str, cron_expression: str, is_active: bool, info: str = None):
        self.name = name
        self.cron_expression = cron_expression
        self.is_enabled = is_active
        self.info = info


TEMP_DIR_CLEANUP = Timer('temp_dir_cleanup', Env.CRON_TEMP_DIR_CLEANUP.get(),
                         Env.ENABLE_TIMER_TEMP_DIR_CLEANUP.get_bool())
REDDIT_POST_ONE_PIECE = Timer('reddit_post_one_piece', Env.CRON_REDDIT_POST_ONE_PIECE.get(),
                              Env.ENABLE_TIMER_REDDIT_POST_ONE_PIECE.get_bool(),
                              info=Env.REDDIT_ONE_PIECE_SUBREDDIT.get())
REDDIT_POST_MEME_PIECE = Timer('reddit_post_meme_piece', Env.CRON_REDDIT_POST_MEME_PIECE.get(),
                               Env.ENABLE_TIMER_REDDIT_POST_MEME_PIECE.get_bool(),
                               info=Env.REDDIT_MEME_PIECE_SUBREDDIT.get())
TIMER_SEND_LEADERBOARD = Timer('timer_send_leaderboard', Env.CRON_SEND_LEADERBOARD.get(),
                               Env.ENABLE_TIMER_SEND_LEADERBOARD.get_bool())
RESET_DOC_Q_GAME = Timer('reset_doc_q_game', Env.CRON_RESET_DOC_Q_GAME.get(),
                         Env.ENABLE_TIMER_RESET_DOC_Q_GAME.get_bool())
RESET_BOUNTY_POSTER_LIMIT = Timer('reset_bounty_poster_limit', Env.CRON_RESET_BOUNTY_POSTER_LIMIT.get(),
                                  Env.ENABLE_TIMER_RESET_BOUNTY_POSTER_LIMIT.get_bool())
RESET_CAN_CHANGE_REGION = Timer('reset_can_change_region', Env.CRON_RESET_CAN_CHANGE_REGION.get(),
                                Env.ENABLE_TIMER_RESET_CAN_CHANGE_REGION.get_bool())
ADD_REGION_BOUNTY = Timer('add_region_bounty', Env.CRON_ADD_REGION_BOUNTY.get(),
                          Env.ENABLE_TIMER_ADD_REGION_BOUNTY.get_bool())
RESET_CAN_INITIATE_GAME = Timer('reset_can_initiate_game', Env.CRON_RESET_CAN_INITIATE_GAME.get(),
                                Env.ENABLE_TIMER_RESET_CAN_INITIATE_GAME.get_bool())

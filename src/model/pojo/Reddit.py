import praw


class Reddit:
    def __init__(self, client_id, client_secret, user_agent):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.connection = praw.Reddit(client_id=self.client_id,
                                      client_secret=self.client_secret,
                                      user_agent=self.user_agent)

    def get_subreddit_hot_posts(self, subreddit, limit=10) -> list:
        return self.connection.subreddit(subreddit).hot(limit=limit)

import praw


class BaseJob:
    """Base class for defining a single working item for the bot.
    Current suported implementations are:
    (a) PostJob: A Post from an activated sub-reddit
    (b) CommentJob: A mention of the bot via /u/[botname] in the comment section of a post
    """

    def get_post(self) -> praw.Reddit.post:
        raise NotImplementedError()

    def reply(self, comment: str) -> None:
        raise NotImplementedError()


class PostJob(BaseJob):
    def __init__(self, post: praw.Reddit.post) -> None:
        self.post = post

    def get_post(self) -> praw.Reddit.post:
        return self.post

    def reply(self, comment: str) -> None:
        self.post.reply(comment)


class CommentJob(BaseJob):
    def __init__(self, comment: praw.Reddit.comment) -> None:
        self.comment = comment

    def get_post(self) -> praw.Reddit.post:
        return self.comment.submission

    def reply(self, comment: str) -> None:
        self.comment.reply(comment)

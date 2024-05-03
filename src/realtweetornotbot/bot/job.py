import praw

class BaseJob:
    """ Base class for defining a single working item for the bot. 
    Current suported implementations are:
    (a) PostJob: A Post from an activated sub-reddit
    (b) CommentJob: A mention of the bot via /u/[botname] in the comment section of a post
    """
    
    def get_post(self) -> praw.Reddit.post:
        raise NotImplementedError()
    
    
class PostJob(BaseJob):
    def __init__(self, post: praw.Reddit.post) -> None:
        super.__init__()
        self.post = post
    
    def get_post(self) -> praw.Reddit.post:
        return self.post
    

class CommentJob(BaseJob):
    def __init__(self, comment: praw.Reddit.comment) -> None:
        super.__init__()
        self.comment = comment
        
        
    def get_post(self) -> praw.Reddit.post:
        return self.comment.submission

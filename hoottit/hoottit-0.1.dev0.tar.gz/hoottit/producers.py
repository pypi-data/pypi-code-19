"""The producers module exposes functions that return generators that produce
data, as opposed from consumers.
"""

# standard library
import datetime

# third party
import praw

# hoottit
import hoottit.util


def _make_stream(sitename, subreddits):
    """This simple function takes in a sitename and a list of subreddits and
    returns a praw stream object.
    """
    user_agent = hoottit.util.make_user_agent('0.0', sitename)
    reddit = praw.Reddit(sitename, user_agent=user_agent)
    subreddit = reddit.subreddit('+'.join(subreddits))
    return subreddit.stream


def comments(subreddits):
    """Yield comments from a subreddit stream.

    This function returns a generator that yields values from a subreddit
    stream.
    """
    stream = _make_stream('hoottit', subreddits)
    for comment in stream.comments():
        yield {
            'reddit_id': comment.id,
            'parent_id': comment.parent_id,
            'body': comment.body,
            'permalink': hoottit.util.remove_parameters(comment.permalink()),
            'subreddit': comment.subreddit.display_name,
            'created': datetime.datetime.utcfromtimestamp(comment.created_utc),
            'cached': datetime.datetime.utcnow(),
            'nsfw': comment.over_18
        }


def submissions(subreddits):
    """Same as comments, but for submissions."""
    stream = _make_stream('barron', subreddits)
    for submission in stream.submissions():
        yield {
            'reddit_id': submission.id,
            'title': submission.title,
            'body': submission.selftext,
            'shortlink': hoottit.util.remove_parameters(submission.shortlink),
            'permalink': hoottit.util.remove_parameters(submission.permalink),
            'subreddit': submission.subreddit.display_name,
            'created': datetime.datetime.utcfromtimestamp(submission.created_utc),
            'cached': datetime.datetime.utcnow(),
            'nsfw': submission.over_18
        }

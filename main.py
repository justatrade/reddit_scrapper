# скрипт, который спрашивает сабреддит, парсит с него все посты за последние 3 дня
# и выводит топ пользователей, которые написали больше всего комментариев и
# топ пользователей, которые написали больше всего постов.
# Топ - это когда сверху тот, кто больше всех написал комментариев/постов,
# на втором месте следущий за ним и так далее.

import calendar
from collections import Counter
from _datetime import datetime
from datetime import timedelta
import time

import praw
from praw.models.comment_forest import CommentForest
from praw.models.reddit.submission import Submission
from prawcore.exceptions import TooManyRequests

import config


def count_subcomments(thread: CommentForest,
                      comments_authors: dict[str, int]) -> None:
    """
    Counts comments of particular author by one and skips deleted ones
    :param thread: CommentForest of submission with all-level comments
    :param comments_authors: Dictionary of authors and their comments
    :return:
    """
    for each in thread.list():
        if each.author:
            current_comments = comments_authors.get(each.author.name, 0) + 1
            comments_authors[each.author.name] = current_comments


def print_results(finish_time:float, start_time:float,
                  posts_authors:dict[str, int]=None,
                  comments_authors:dict[str, int]=None,
                  submissions_dict:dict[str, int]=None)-> None:
    if posts_authors:
        print('Most posts created')
        pretty_out(posts_authors)
    if comments_authors:
        print('Most comments posted')
        pretty_out(comments_authors)
    if submissions_dict:
        print('Most commented topics')
        pretty_out(submissions_dict)

    print(f'Total time: {finish_time - start_time}s')


def get_all_sub_comments(thread: Submission, comments_authors) -> int:
    """
    Expands all comments with its replies and processing counting.
    :param thread: Submission (thread) of subreddit
    :param comments_authors: Dictionary for counting comments of particular
    authors
    :return: Total number of comments in suubmission
    """
    try:
        thread.comments.replace_more(limit=None)
        count_subcomments(thread.comments, comments_authors)
    except TooManyRequests:
        time.sleep(3)
        thread.comments.replace_more(limit=None)
        count_subcomments(thread.comments, comments_authors)
    return len(thread.comments.list())


def pretty_out(to_print: dict[str, int]) -> None:
    """
    Prints dictionary with top 10 most common results of dictionary with
    str as key and int as value
    :param to_print:
    :return:
    """
    for i, user in enumerate(Counter(to_print).most_common(10)):
        print(f'{i+1}. {user[0]} - {user[1]}')


def process_comment_counting() -> None:
    """
    Main processing function
    :return:
    """
    posts_authors: dict[str, int] = {}
    comments_authors: dict[str, int] = {}
    submissions_dict: dict[str, int] = {}

    start_time = time.time()

    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent
    )
    submissions = reddit.subreddit(config.SUBMISSION).top(time_filter='week')
    oldest_utc = datetime.utcnow() - timedelta(days=config.TIME_DEPTH_DAYS)
    oldest_utc = calendar.timegm(oldest_utc.utctimetuple())
    for each in submissions.__iter__():
        if each.created_utc > oldest_utc:
            current_posts = posts_authors.get(each.author.name, 0) + 1
            posts_authors[each.author.name] = current_posts
            print(f'{datetime.utcnow()} '
                  f'[INFO] Processing submission: {each.title}')
            submissions_dict[each.title] = get_all_sub_comments(each, comments_authors)
            time.sleep(0.5)

    finish_time = time.time()
    print_results(finish_time, start_time,
                  posts_authors, comments_authors, submissions_dict)

if __name__ == '__main__':
    process_comment_counting()

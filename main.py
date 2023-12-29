# скрипт, который спрашивает сабреддит, парсит с него все посты за последние 3 дня
# и выводит топ пользователей, которые написали больше всего комментариев и
# топ пользователей, которые написали больше всего постов.
# Топ - это когда сверху тот, кто больше всех написал комментариев/постов,
# на втором месте следущий за ним и так далее.

import calendar
import sys
import time

import praw

import config

from collections import Counter
from datetime import datetime, timedelta

from praw.models.comment_forest import CommentForest
from praw.models.reddit.submission import Submission
from prawcore.exceptions import NotFound
from prawcore.exceptions import TooManyRequests



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
        time.sleep(0.8)
        thread.comments.replace_more(limit=None)
        count_subcomments(thread.comments, comments_authors)
    return len(thread.comments.list())


def user_input_subreddit() -> str:
    """
    Getting the name of subreddit to parse
    :return:
    """
    subreddit = input('Subreddit to search: ')
    return subreddit


def user_input_time_frame() -> dict[str, int]:
    """
    Get user specified time frame for search and check it's validness
    :return: Dictionary of weeks, days, hours for using in timedelta()
    """
    time_frame = input('Time_frame of your search '
                       '[number] [hours/days/weeks]: ')
    try:
        number = int(time_frame.split()[0])
        period = str(time_frame.split()[1])
        if period not in ['hours', 'days', 'weeks'] or number < 1:
            raise ValueError
    except ValueError:
        print('Try to be more accurate... Next time!)')
        sys.exit(0)
    weeks = days = hours = 0
    if period == 'hours':
        weeks = number // 168
        days = (number - weeks * 168) // 24
        hours = (number - weeks * 168 - days * 24) % 24
    elif period == 'days':
        weeks = number // 7
        days = (number - weeks * 7) % 7
    else:
        weeks = number
    return {'weeks': weeks, 'days': days, 'hours': hours}


def pretty_out(to_print: dict[str, int]) -> None:
    """
    Prints dictionary with top 10 most common results of dictionary with
    str as key and int as value
    :param to_print:
    :return:
    """
    for i, elem in enumerate(Counter(to_print).most_common(10)):
        print(f'{i+1}. {elem[0]} - {elem[1]}')


def subreddit_exists(reddit, subreddit) -> bool:
    """
    Checks the availability of subreddit
    :param reddit: Instance of reddit
    :param subreddit: Name of subreddit to check
    :return:
    """
    exists = True
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
    except NotFound:
        exists = False
    return exists


def process_comment_counting() -> None:
    """
    Main processing function
    :return:
    """
    posts_authors: dict[str, int] = {}
    comments_authors: dict[str, int] = {}
    submissions_dict: dict[str, int] = {}

    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent
    )
    subreddit = user_input_subreddit()

    while not subreddit_exists(reddit, subreddit):
        subreddit = user_input_subreddit()

    start_time = time.time()
    submissions = reddit.subreddit(subreddit).top(time_filter='year',
                                                  limit=None)
    time_frame = user_input_time_frame()

    oldest_utc = datetime.utcnow() - timedelta(**time_frame)
    oldest_utc = calendar.timegm(oldest_utc.utctimetuple())
    submissions_len = 0
    for each in submissions.__iter__():
        if each.created_utc > oldest_utc:
            submissions_len += 1
            current_posts = posts_authors.get(each.author.name, 0) + 1
            posts_authors[each.author.name] = current_posts
            print(f'{datetime.utcnow()} '
                  f'[INFO] Processing submission: {each.title}')
            submissions_dict[each.title] = get_all_sub_comments(each, comments_authors)
            time.sleep(0.2)
    print(f'Total submissions processed: {submissions_len}')
    finish_time = time.time()
    print_results(finish_time, start_time,
                  posts_authors, comments_authors, submissions_dict)
    print(f'Total authors: {len(comments_authors)}')
    print(f'Total comments: {sum(list(comments_authors.values()))}')


if __name__ == '__main__':
    process_comment_counting()

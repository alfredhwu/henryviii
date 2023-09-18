"""
package henryviii.model.article

this defines the operation for off_acount article
"""

from flask import current_app

from henryviii.db import get_db
from henryviii.model import (
    user_category as model_user_category,
    filter as model_filter
    )


def get_all_article_with_user_category(username, user_category_list, page_size=50, page=0):
    """
    Get all article list with user_category

    user_category in TABLE off_account_user_meta, as recored with COLUMN category
    article in TABLE off_account_article, connect with off_accouht with off_account_name

    :username: name for user
    :user_category_list: list of user_category
    :page_size: limit of result count, default set to 50
    :page: # of page to display, from 0
    :return: list of { attr: value }
    """
    user_category_filter = [user_category for user_category in user_category_list]
    return get_all_article_by_user_filter(username, {
        "user_category_filter": user_category_filter
        },
        page_size, page)

def get_all_article_by_user_filter(username, user_filter, page_size, page=0):

    user_category_filter = user_filter["user_category"]

    # TEST SCENARIO for user_category
    # user_category_filter = None
    # user_category_filter = []
    # user_category_filter = ['_default']
    # user_category_filter = ['_default', '科技']
    # user_category_filter = ['科技']
    # user_category_filter = ['科技', 'AI']

    # current_app.logger.debug(get_user_category_filter_sql(None)) 
    # current_app.logger.debug(get_user_category_filter_sql([])) 
    # current_app.logger.debug(get_user_category_filter_sql([model_user_category.__DEFAULT_USER_CATEGORY__])) 
    # current_app.logger.debug(get_user_category_filter_sql([model_user_category.__DEFAULT_USER_CATEGORY__, '科技'])) 
    # current_app.logger.debug(get_user_category_filter_sql(['AI', '科技'])) 

    articles = get_db().execute(
        'SELECT oaa.off_account_name, oaa.id, oaa.title, STRFTIME("%m/%d %H:%M", oaa.updated_at) as updated_at, oaa.link, oaum.user_category, oaav.updated_at as viewed_at'
        ' FROM off_account_article oaa'
        ' LEFT JOIN off_account_user_meta oaum'
        ' ON oaa.off_account_name = oaum.off_account_name'
        ' LEFT JOIN off_account_article_viewed oaav'
        ' ON oaa.id = oaav.off_account_article_id'
        ' WHERE oaum.username = ?'
        ' ' + get_user_category_filter_sql(user_filter["user_category"]) + ''
        ' ' + get_datetime_from_filter_sql(user_filter["date_from"]) + ''
        ' ' + get_datetime_to_filter_sql(user_filter["date_to"]) + ''
        ' ' + get_view_status_filter_sql(user_filter["view_status"]) + ''
        ' ' + get_archive_status_filter_sql(user_filter["archive_status"]) + ''
        ' ' + get_favorite_status_filter_sql(user_filter["favorite_status"]) + ''
        ' ORDER BY oaa.updated_at DESC, oaa.off_account_name ASC, oaa.title ASC'
        ' LIMIT ?'
        ' OFFSET ?',
        (username, page_size, page_size * page)
    ).fetchall()
    # current_app.logger.debug(f"page_size: { page_size }, page: { page }")
    return articles

def get_datetime_from_filter_sql(datetime_from):
    return f' AND oaa.updated_at >= "{ datetime_from }"'


def get_datetime_to_filter_sql(datetime_to):
    return f' AND oaa.updated_at <= "{ datetime_to }"'


"""
status filter
"""
def get_view_status_filter_sql(view_filter):
    match view_filter:
        case model_filter.__STATUS_VIEWED__:
            return f' AND oaav.updated_at NOT NULL'
        case model_filter.__STATUS_NOT_VIEWED__:
            return f' AND oaav.updated_at IS NULL'
        case _:
            return ""


def get_favorite_status_filter_sql(favorite_filter):
    return ""


def get_archive_status_filter_sql(archive_filter):
    return ""

"""
User_category filter
"""

def get_in_operation_sql_from_list(filter_key, filter_list):
    if not filter_list or len(filter_list) ==0:
        return ""
    inner_sql_string = '", "'.join(filter_list)
    return f'{ filter_key } IN ("{ inner_sql_string }")'

def get_user_category_filter_sql(user_category_filter):

    if not user_category_filter or len(user_category_filter) == 0: 
        ## no need to filter by user_category, return all
        filter_sql = ''
    elif model_user_category.__DEFAULT_USER_CATEGORY__ in user_category_filter: ## need to consider NULL in sql
        ## default user category is null in db, needs special care
        if len(user_category_filter) == 1: 
            ## only '_default' in the list
            filter_sql = f' AND oaum.user_category IS NULL'
        else:
            ## remove '_default' from the list
            user_category_filter.remove(model_user_category.__DEFAULT_USER_CATEGORY__)
            filter_sql = f' AND (oaum.user_category IS NULL OR { get_in_operation_sql_from_list("oaum.user_category", user_category_filter) })'
    else:
        filter_sql = f' AND ({ get_in_operation_sql_from_list("oaum.user_category", user_category_filter) })'
    return filter_sql



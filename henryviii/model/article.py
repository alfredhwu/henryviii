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

from datetime import datetime

# def get_all_article_with_user_category(username, user_category_list, page_size=50, page=0):
#     """
#     Get all article list with user_category

#     user_category in TABLE off_account_user_meta, as recored with COLUMN category
#     article in TABLE off_account_article, connect with off_accouht with off_account_name

#     :username: name for user
#     :user_category_list: list of user_category
#     :page_size: limit of result count, default set to 50
#     :page: # of page to display, from 0
#     :return: list of { attr: value }
#     """
#     user_category_filter = [user_category for user_category in user_category_list]
#     return get_all_article_by_user_filter(username, {
#         "user_category_filter": user_category_filter
#         },
#         page_size, page)

def get_all_article_by_user_filter(username, user_filter, page_size, page=0):

    # user_category_filter = user_filter["user_category"]

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

    # articles = get_db().execute(
    #     'SELECT oaa.off_account_name, oaum.off_account_id, oaa.id, oaa.title, STRFTIME("%m/%d %H:%M", oaa.updated_at) as updated_at, oaa.link, oaum.user_category, oaaum.viewed_at, oaaum.liked_at, oaaum.disliked_at, oaaum.deleted_at, oaaum.archived_at'
    #     ' FROM off_account_article oaa'
    #     ' LEFT JOIN off_account_user_meta oaum'
    #     ' ON oaa.off_account_name = oaum.off_account_name'
    #     ' LEFT JOIN off_account_article_user_meta oaaum'
    #     ' ON oaa.id = oaaum.off_account_article_id'
    #     ' WHERE oaum.username = ?'
    #     ' AND oaaum.deleted_at IS NULL'
    #     ' ' + get_off_account_id_filter_sql(user_filter, "off_account_id") + ''
    #     ' ' + get_user_category_filter_sql(user_filter, "user_category") + ''
    #     ' ' + get_datetime_from_filter_sql(user_filter, "date_from") + ''
    #     ' ' + get_datetime_to_filter_sql(user_filter, "date_to") + ''
    #     ' ' + get_view_status_filter_sql(user_filter, "view_status") + ''
    #     ' ' + get_archive_status_filter_sql(user_filter, "archive_status") + ''
    #     ' ' + get_favorite_status_filter_sql(user_filter, "favorite_status") + ''
    #     ' ORDER BY oaa.updated_at DESC, oaa.off_account_name ASC, oaa.title ASC'
    #     ' LIMIT ?'
    #     ' OFFSET ?',
    #     (username, page_size, page_size * page)
    # ).fetchall()


    # current_app.logger.debug(user_filter)

    sql_str = f"""
        SELECT oaa.off_account_name, oaum.off_account_id, oaa.id, oaa.title, STRFTIME("%m/%d %H:%M", oaa.updated_at) as updated_at, oaa.link, oaum.user_category, oaaum.viewed_at, oaaum.liked_at, oaaum.disliked_at, oaaum.deleted_at, oaaum.archived_at
         FROM off_account_article oaa
         LEFT JOIN off_account_user_meta oaum
         ON oaa.off_account_name = oaum.off_account_name
         LEFT JOIN off_account_article_user_meta oaaum
         ON oaa.id = oaaum.off_account_article_id
         WHERE oaum.username = "{ username }"
         AND oaaum.deleted_at IS NULL
         { get_off_account_id_filter_sql(user_filter, "off_account_id") }
         { get_user_category_filter_sql(user_filter, "user_category") }
         { get_datetime_from_filter_sql(user_filter, "date_from") }
         { get_datetime_to_filter_sql(user_filter, "date_to") }
         { get_view_status_filter_sql(user_filter, "view_status") }
         { get_archive_status_filter_sql(user_filter, "archive_status") }
         { get_favorite_status_filter_sql(user_filter, "favorite_status") }
         ORDER BY oaa.updated_at DESC, oaa.off_account_name ASC, oaa.title ASC
         LIMIT { page_size }
         OFFSET { page_size * page };
         """
    # current_app.logger.debug(sql_str)

    articles = get_db().execute(sql_str).fetchall()

    return articles

def get_datetime_from_filter_sql(user_filter, datetime_from_filter):
    return '' if datetime_from_filter not in user_filter else f' AND oaa.updated_at >= "{ user_filter[datetime_from_filter] }"'


def get_datetime_to_filter_sql(user_filter, datetime_to_filter):
    return '' if datetime_to_filter not in user_filter else f' AND oaa.updated_at <= "{ user_filter[datetime_to_filter] }"'


"""
status filter
"""
def get_view_status_filter_sql(user_filter, view_filter):
    if view_filter not in user_filter:
        return ""

    match user_filter[view_filter]:
        case model_filter.__STATUS_VIEWED__:
            return f' AND oaaum.viewed_at NOT NULL'
        case model_filter.__STATUS_NOT_VIEWED__:
            return f' AND oaaum.viewed_at IS NULL'
        case _:
            return ""


def get_favorite_status_filter_sql(user_filter, favorite_filter):
    if favorite_filter not in user_filter:
        return ""

    match user_filter[favorite_filter]:
        case model_filter.__STATUS_FAVORITE__:
            return f' AND oaaum.liked_at NOT NULL'
        case model_filter.__STATUS_NOT_FAVORITE__ :
            return f' AND oaaum.liked_at IS NULL'
        case _:
            return ""


def get_archive_status_filter_sql(user_filter, archive_filter):
    return ""

"""
User_category filter
"""

def get_in_operation_sql_from_list(filter_key, filter_list):
    if not filter_list or len(filter_list) ==0:
        return ""
    inner_sql_string = '", "'.join(filter_list)
    return f'{ filter_key } IN ("{ inner_sql_string }")'

def get_user_category_filter_sql(user_filter, user_category_filter_key):
    if user_category_filter_key not in user_filter:
        return ''

    user_category_filter = user_filter[user_category_filter_key]

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

def get_off_account_id_filter_sql(user_filter, off_account_id_filter):
    if off_account_id_filter not in user_filter or not isinstance(user_filter[off_account_id_filter], int):
        filter_sql = ''
    else:
        filter_sql = f' AND oaum.off_account_id = { user_filter[off_account_id_filter] }'
    return filter_sql

"""
status setters
"""

def set_article_viewed_by_id(username, article_id, viewed=True):
    return set_article_status_by_id(username, article_id, "viewed", viewed)

def set_article_liked_by_id(username, article_id, liked=True):
    return set_article_status_by_id(username, article_id, "liked", liked)

def set_article_disliked_by_id(username, article_id, disliked=True):
    pass

def set_article_deleted_by_id(username, article_id, deleted=True):
    return set_article_status_by_id(username, article_id, "deleted", deleted)

def set_article_status_by_id(username, article_id, status, activate=True):
    """
    :param status: viewed|liked|disliked|deleted
    """
    if status not in ['viewed', 'liked', 'disliked', 'deleted']:
        return False
    db = get_db()
    ## create if not exists
    db.execute('INSERT OR IGNORE INTO off_account_article_user_meta (username, off_account_article_id)'
                ' VALUES (?, ?)',
                (username, article_id))
    set_str = f' SET {status}_at = ?'
    status_str = None if not activate else datetime.now().strftime('%Y-%m-%d %X')
    db.execute('UPDATE off_account_article_user_meta'
                '' + set_str + ''
                ' WHERE username = ?'
                ' AND off_account_article_id = ?',
                (status_str, username, article_id))
    db.commit()
    return True


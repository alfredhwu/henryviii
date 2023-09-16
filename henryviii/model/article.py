"""
package henryviii.model.article

this defines the operation for off_acount article
"""

from flask import current_app

from henryviii.db import get_db
from henryviii.model import user_category as model_user_category

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

def get_all_article_with_user_category(username, user_category_list, limit_count=10):
    """
    Get all article list with user_category

    user_category in TABLE off_account_user_meta, as recored with COLUMN category
    article in TABLE off_account_article, connect with off_accouht with off_account_name

    :username: name for user
    :user_category_list: list of user_category
    :return: list of { attr: value }
    """
    user_category_filter = [user_category for user_category in user_category_list]


    # TEST SCENARIO
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
        ' ' + get_user_category_filter_sql(user_category_filter) + ''
        ' ORDER BY oaa.updated_at DESC, oaa.off_account_name ASC, oaa.title ASC'
        ' LIMIT ?',
        (username, limit_count,)
    ).fetchall()
    return articles
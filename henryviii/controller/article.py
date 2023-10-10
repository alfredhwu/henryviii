from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.model import current_user
from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    article as model_article,
    filter as model_filter
)

from henryviii.db import get_db
from datetime import date, datetime


__FILTER_USER_CATEGORY__    = "uc"
__FILTER_VIEW_STATUS__      = "view"
__FILTER_FAVORITE_STATUS__  = "fav"
__FILTER_ARCHIVE_STATUS__   = "arc"
__FILTER_DATE_FROM__        = "dtf"
__FILTER_DATE_TO__          = "dtt"

bp = Blueprint('article', __name__)

@bp.before_app_request
def load_logged_in_user():
    g.user = current_user.get_current_user()

# @bp.route('/', methods=('GET', 'POST'))
# @login_required
# def index_controller():
#     db = get_db()

#     # get off_account dictionary
#     off_account_dict = model_off_account_user_category.get_dict_of_user_category_with_following_off_account(g.user["username"])

#     # update filter if POST method
#     if request.method == 'POST':
#         category_selected = []
#         for category in off_account_dict:
#             if request.form.get(category):
#                 category_selected.append(category)
#     else:
#         category_selected = off_account_dict.keys()

#     filter_user_category = category_selected
#     articles = model_article.get_all_article_with_user_category(g.user["username"], filter_user_category, 50)

#     return render_template('articles/index.html', 
#         off_account_dict=off_account_dict, 
#         filter_user_category=filter_user_category,  # filter category
#         articles=articles)

@bp.route('/article/<int:id>/view', methods=['POST'])
@login_required
def view(id):
    # db = get_db()
    # ## find article by id
    # find_article_by_id = db.execute(
    #     'SELECT * FROM off_account_article WHERE id=' + str(id)
    # ).fetchone()
    # if not find_article_by_id:
    #     return { "status": "failure", "message": "article not found" }

    # username = g.user["username"]
    # db.execute(
    #     'INSERT OR IGNORE INTO off_account_article_user_meta (off_account_article_id, username, viewed_at)'
    #     ' VALUES (?, ?, ?)',
    #     (id, username, datetime.now().strftime('%Y-%m-%d %X'))
    # )
    # db.commit()
    # return { "status": "success", "message": "article view recorded"}
    if model_article.set_article_viewed_by_id(g.user["username"], id):
        return { "status": "success", "message": "successfully viewed the article" }

    return { "status": "failure", "message": "oops, something went wrong, failed to view the article"}


@bp.route('/article/liked')
@login_required
def index_controller():

    # get off_account dictionary
    off_account_dict = model_off_account_user_category.get_dict_of_user_category_with_following_off_account(g.user["username"])

    dash_filter = get_dash_filter()
    current_app.logger.debug(dash_filter)

    # articles = model_article.get_all_article_by_user_filter(
    #     g.user["username"],
    #     {
    #         "favorite_status": model_filter.__STATUS_FAVORITE__
    #     },
    #     page_size=50, page=0)
    articles = model_article.get_all_article_by_user_filter(
        g.user["username"],
        dash_filter,
        page_size=50, page=0)
    # current_app.logger.debug(articles)
    return render_template("off_accounts/page.html", 
        off_account_dict=off_account_dict, 
        dash_filter=dash_filter,
        articles=articles,
        status_map={
            "view": {
                model_filter.__STATUS_ALL__: "全部", 
                model_filter.__STATUS_VIEWED__: "已读", 
                model_filter.__STATUS_NOT_VIEWED__: "未读"
            }
        })


@bp.route('/article/liked/more/article/<int:page_size>/<int:page>')
@login_required
def render_article(page_size, page):
    ## with dash_filter
    dash_filter = get_dash_filter()
    current_app.logger.debug(dash_filter)
    ## with pagination 
    # dash_filter["page_size"] = request.args.get("size", 50, type=int)
    # dash_filter["page"] = request.args.get("page", 0, type=int)

    articles = model_article.get_all_article_by_user_filter(
        g.user["username"],
        dash_filter,
        page_size=page_size, page=page)
    return render_template('dashboard/more_articles.html', articles=articles)


def get_dash_filter():
    dash_filter = {}
    dash_filter["user_category"] = model_filter.parse("user_category", request.args.get(__FILTER_USER_CATEGORY__, "", type=str))
    dash_filter["view_status"] = model_filter.parse("view_status", request.args.get(__FILTER_VIEW_STATUS__, type=int))
    dash_filter["favorite_status"] = model_filter.__STATUS_FAVORITE__
    # dash_filter["favorite_status"] = model_filter.parse("favorite_status", request.args.get(__FILTER_FAVORITE_STATUS__, type=int))
    dash_filter["archive_status"] = model_filter.parse("archive_status", request.args.get(__FILTER_ARCHIVE_STATUS__, type=int))
    dash_filter["date_from"] = model_filter.parse("date_from", request.args.get(__FILTER_DATE_FROM__, "", type=str))
    dash_filter["date_to"] = model_filter.parse("date_to", request.args.get(__FILTER_DATE_TO__, "", type=str))
    return dash_filter

@bp.route('/article/<int:id>/like', methods=['POST'])
@login_required
def like(id):
    if model_article.set_article_liked_by_id(g.user["username"], id):
        return { "status": "success", "message": "successfully liked the article" }

    return { "status": "failure", "message": "oops, something went wrong, failed to like the article"}


@bp.route('/article/<int:id>/like/cancel', methods=['POST'])
@login_required
def cancel_like(id):
    if model_article.set_article_liked_by_id(g.user["username"], id, False):
        return { "status": "success", "message": "successfully cancel the liked status for the article" }

    return { "status": "failure", "message": "oops, something went wrong, failed to cancel the liked status for the article"}

@bp.route('/article/<int:id>/dislike', methods=['POST'])
@login_required
def dislike(id):
    pass


@bp.route('/article/<int:id>/dislike/cancel', methods=['POST'])
@login_required
def cancel_dislike(id):
    pass


@bp.route('/article/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if model_article.set_article_deleted_by_id(g.user["username"], id):
        return { "status": "success", "message": "successfully deleted the article" }

    return { "status": "failure", "message": "oops, something went wrong, failed to delete the article"}






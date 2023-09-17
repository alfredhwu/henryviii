from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.model import current_user
from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    article as model_article
)

from henryviii.db import get_db
from henryviii.model import filter as model_filter
from datetime import date, datetime


__FILTER_USER_CATEGORY__    = "uc"
__FILTER_VIEW_STATUS__      = "view"
__FILTER_FAVORITE_STATUS__  = "fav"
__FILTER_ARCHIVE_STATUS__   = "arc"
__FILTER_DATE_FROM__        = "dtf"
__FILTER_DATE_TO__          = "dtt"

bp = Blueprint('dashboard', __name__)

@bp.before_app_request
def load_logged_in_user():
    g.user = current_user.get_current_user()

@bp.route('/')
@login_required
def dashboard_controller():
    db = get_db()


    # get off_account dictionary
    off_account_dict = model_off_account_user_category.get_dict_of_user_category_with_following_off_account(g.user["username"])

    dash_filter = get_dash_filter()

    ## if pagination
    dash_mode = request.args.get("mode", "scroll", type=str)

    articles = model_article.get_all_article_by_user_filter(
        g.user["username"],
        dash_filter,
        page_size=50, page=0)

    return render_template('dashboard/index.html', 
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


@bp.route('/more/article/<int:page_size>/<int:page>')
@login_required
def render_article(page_size, page):
    ## with dash_filter
    dash_filter = get_dash_filter()
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
    dash_filter["favorite_status"] = model_filter.parse("favorite_status", request.args.get(__FILTER_FAVORITE_STATUS__, type=int))
    dash_filter["archive_status"] = model_filter.parse("archive_status", request.args.get(__FILTER_ARCHIVE_STATUS__, type=int))
    dash_filter["date_from"] = model_filter.parse("date_from", request.args.get(__FILTER_DATE_FROM__, "", type=str))
    dash_filter["date_to"] = model_filter.parse("date_to", request.args.get(__FILTER_DATE_TO__, "", type=str))
    return dash_filter


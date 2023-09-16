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
from datetime import date, datetime

bp = Blueprint('article', __name__)

@bp.before_app_request
def load_logged_in_user():
    g.user = current_user.get_current_user()

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index_controller():
    db = get_db()

    # get off_account dictionary
    off_account_dict = model_off_account_user_category.get_dict_of_user_category_with_following_off_account(g.user["username"])

    # update filter if POST method
    if request.method == 'POST':
        category_selected = []
        for category in off_account_dict:
            if request.form.get(category):
                category_selected.append(category)
    else:
        category_selected = off_account_dict.keys()

    filter_user_category = category_selected
    articles = model_article.get_all_article_with_user_category(g.user["username"], filter_user_category, 10)

    return render_template('articles/index.html', 
        off_account_dict=off_account_dict, 
        filter_user_category=filter_user_category,  # filter category
        articles=articles)

@bp.route('/article/<int:id>/view', methods=['POST'])
@login_required
def view(id):
    db = get_db()
    ## find article by id
    find_article_by_id = db.execute(
        'SELECT * FROM off_account_article WHERE id=' + str(id)
    ).fetchone()
    if not find_article_by_id:
        return { "status": "failed", "message": "article not found" }

    username = g.user["username"]
    db.execute(
        'INSERT OR IGNORE INTO off_account_article_viewed (off_account_article_id, username, updated_at)'
        ' VALUES (?, ?, ?)',
        (id, username, datetime.now().strftime('%Y-%m-%d %X'))
    )
    db.commit()
    return { "status": "success", "message": "article view recorded"}

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.db import get_db

# import xlrd
from openpyxl import Workbook, load_workbook
import pandas as pd
from datetime import date, datetime

bp = Blueprint('article', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def get_followed_off_account_list():
    db = get_db()
    oa_list = []
    for row in db.execute(
        'SELECT off_account_name'
        ' FROM off_account_followed'
        ' WHERE username="' + g.user["username"] + '"'
        ).fetchall():
        oa_list.append(row["off_account_name"])
    return oa_list

@bp.route('/sync')
@login_required
def sync():

    return redirect(url_for("index"))

# def get_form_value(form_key):
#     if request.form.get(form_key):
#         return request.form.get(form_key)
#     elif 'form_data' in session:
#         return session['form_data'].get(form_key)
#     return None

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()

    ## restore form data from session

    ## get off account dictionary
    off_account_dict = dict()
    off_account_list = []
    for oa in db.execute(
        'SELECT oal.name, oal.category'
        ' FROM off_account_followed oaf'
        ' LEFT JOIN off_account_list oal'
        ' ON oal.name = oaf.off_account_name'
        ' WHERE oaf.username = "' + g.user["username"] + '"'
        ).fetchall():
        current_category = oa["category"]
        current_account_name = oa["name"]
        if current_category not in off_account_dict:
            off_account_dict[current_category]=[current_account_name]
        else:
            off_account_dict[current_category].append(current_account_name)
        off_account_list.append(current_account_name)

    if request.method == 'POST':
        off_account_selected = []
        category_selected = []
        # for off_account in off_account_list:
        #     if request.form.get(off_account): ## here need more inspect
        #         off_account_selected.append(off_account)
        for category in off_account_dict:
            if request.form.get(category):
                category_selected.append(category)
    else:
        off_account_selected = off_account_list
        category_selected = off_account_dict.keys()

    ## retrieve articles
    articles = db.execute(
        'SELECT oaa.off_account_name, oaa.id, oaa.title, STRFTIME("%m/%d %H:%M", oaa.updated_at) as updated_at, oaa.link, oal.category, oaav.updated_at as viewed_at'
        ' FROM off_account_article oaa'
        ' LEFT JOIN off_account_list oal'
        ' ON oaa.off_account_name = oal.name'
        ' LEFT JOIN off_account_article_viewed oaav'
        ' ON oaa.id = oaav.off_account_article_id'
        # ' WHERE oal.name IN ' + '("' + '", "'.join(off_account_selected) + '")'
        ' WHERE oal.category IN ' + '("' + '", "'.join(category_selected) + '")'
        ' ORDER BY oaa.updated_at DESC, off_account_name ASC, title ASC'
        ' LIMIT 50'
    ).fetchall()

    return render_template('articles/index.html', off_account_dict=off_account_dict, off_account_selected=off_account_selected, category_selected=category_selected, articles=articles)

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


# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/create.html')


# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post


# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/update.html', post=post)


# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index'))
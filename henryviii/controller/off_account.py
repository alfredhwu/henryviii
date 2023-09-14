from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.db import get_db

from datetime import datetime

bp = Blueprint('off_account', __name__)

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

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = get_db()
    off_accounts = db.execute(
        # 'SELECT oa.id, oa.name, oa.category, oaf.active as followed'
        # ' FROM off_account_followed oaf'
        # ' RIGHT JOIN off_account_list oa'
        # ' WHERE username="' + g.user["username"] + '"'
        'SELECT *'
        ' FROM off_account_list oa'
    ).fetchall()

    ## retrieve current followed status from db
    followed_off_account_list = get_followed_off_account_list()
    # followed_off_account_list = []
    # for row in get_followed_off_accounts():
    #     followed_off_account_list.append(row["off_account_name"])

    if request.method == 'POST':
        for row in off_accounts:
            ## retrieve form info
            if request.form.get(row["name"]) is None and row["name"] in followed_off_account_list:
                ## unfollow the off account
                db.execute(
                    'DELETE FROM off_account_followed'
                    ' WHERE off_account_name="' + row["name"] + '"'
                    ' AND username="' + g.user["username"] + '"'
                )
            if request.form.get(row["name"]) is not None and row["name"]not in followed_off_account_list:
                ## follow the off account
                db.execute(
                    'INSERT INTO off_account_followed (off_account_name, username, updated_at)'
                    ' VALUES (?, ?, ?)',
                    (row["name"], g.user["username"], datetime.now().strftime('%Y-%m-%d %X'))
                )
            continue
        db.commit()
        # flash("post requested")

    return render_template('off_accounts/index.html', off_accounts=off_accounts, followed=get_followed_off_account_list())

@bp.route('/<int:id>/follow', methods=['GET', 'POST'])
@login_required
def follow():
    ## get off account name
    ## get username
    return redirect(url_for('index'))

# @bp.route('/follows')
# @login_required
# def get_follows():

#     return redirect(url_for('index'))

# @bp.route('/follows/update', methods=['POST'])
# @login_required
# def update_follows():
#     if request.method == 'POST':
#         ## retrieve form info
#         ## update database
#         pass
#     ## redirect to display
#     return redirect(url_for('index'))

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
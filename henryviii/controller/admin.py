from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.db import get_db

from openpyxl import Workbook, load_workbook
import pandas as pd
from datetime import datetime

import os

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
def admin():
    return render_template('admin/index.html')

## HERE PROCESS DATA SYNC

ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def sync_file_to_db(filepath):
    db = get_db()
    xlsxname = filepath

    ## sync off_account list
    ## 公众号|分类|是否更新|更新时间|更新文章|备注|登记时间

    ## first get last sync off_account timestamp
    last_off_account = db.execute(
        'SELECT registered_at FROM off_account_list'
        ' ORDER BY id DESC'
        ' LIMIT 1'
    ).fetchone()
    if last_off_account is not None:
        last_off_account_timestamp = 0
    else:
        last_off_account_timestamp = int(last_off_account["registered_at"])

    ## get list of all off_account
    off_accounts_names = {}
    for row in db.execute('SELECT name, article_updated_at FROM off_account_list').fetchall():
        off_accounts_names[row["name"]]=row["article_updated_at"]

    ## iterate uploded file
    for index, row in pd.read_excel(xlsxname, sheet_name="list").iterrows():
        """
        1) new entry, insert new (not in the list)
        2) existing entry with registered_at later than record, pass
        3) existing entry with registered_at before current record, update
        """
        current_name = row["公众号"].strip()
        current_category = row["分类"]
        row_updated_at = row["更新时间"]

        current_updated_at = None
        if isinstance(row_updated_at, datetime):
            # current_updated_at = row["更新时间"].strftime('%Y-%m-%d %X')
            current_updated_at = row_updated_at
            
        else:
            if not pd.isnull(row_updated_at):
                current_updated_at = datetime.strptime(row_updated_at, '%Y年%m月%d日 %H:%M')

        # current_app.logger.debug(pd.isnull(row["登记时间"]))
        current_registered_at = pd.Timestamp.now().timestamp() if pd.isnull(row["登记时间"]) else int(row["登记时间"]) 
        # if row["登记时间"]:
        #     current_registered_at = int(row["登记时间"]) 
        # else: 
        #     current_registered_at = pd.Timestamp.now().timestamp()

        ## if registered before or already in the list
        # if current_registered_at < last_off_account_timestamp or current_name in off_accounts_names:
        if current_name in off_accounts_names:
            ## here can update the update time
            if current_updated_at:
                if not off_accounts_names[current_name] or current_updated_at > pd.Timestamp(off_accounts_names[current_name]):
                    ## update
                    current_app.logger.info(current_name + ":" + current_updated_at.strftime('%Y-%m-%d %X'))
                    db.execute(
                        'UPDATE off_account_list'
                        ' SET article_updated_at = ?'
                        ' WHERE name = ?',
                        (current_updated_at.strftime('%Y-%m-%d %X'), current_name))
            continue
        else:
            ## insert the new off account to the DB
            db.execute(
                'INSERT INTO off_account_list (name, category, article_updated_at, registered_at)'
                ' VALUES (?, ?, ?, ?)',
                (current_name, current_category, current_updated_at.strftime('%Y-%m-%d %X') if current_updated_at else None, current_registered_at)
            )
            off_accounts_names[current_name] = current_updated_at
    ## commit the changes
    db.commit()

    ## sync off_account articles
    ## 公众号|标题|日期|内容|链接|登记时间
    # flash('|'.join(off_account_list_sheet.columns.values))
    last_off_account_article = db.execute(
        'SELECT * FROM off_account_article'
        ' ORDER BY id DESC'
        ' LIMIT 1'
    ).fetchall()
    if len(last_off_account_article)==0:
        last_off_account_article_timestamp = 0
    else:
        last_off_account_article_timestamp = int(last_off_account_article[0]["registered_at"])

    for index, row in pd.read_excel(xlsxname, sheet_name="articles").iterrows():
        if not isinstance(row["链接"], str) or not isinstance(row["内容"], str):
            continue
        current_link = row["链接"].strip()
        current_registered_at = int(row["登记时间"])
        current_off_account_name = row["公众号"].strip()
        current_article_title = row["标题"].strip()

        current_updated_at = None
        if isinstance(row["日期"], datetime):
            current_updated_at = row["日期"].strftime('%Y-%m-%d %X')
        else:
            if row["日期"] is not None:
                current_updated_at = row["日期"].replace('年', '-').replace('月', '-').replace('日', '')
        
        current_content = row["内容"].strip()

        current_app.logger.info(f"{current_article_title} @ {current_updated_at}")

        ## if current_registered_at earlier than the DB record, pass
        if current_registered_at < last_off_account_timestamp:
            continue

        ## if current_link already in DB, pass
        find_article_by_link = db.execute(
            "SELECT * FROM off_account_article WHERE link='" + current_link + "'"
        ).fetchone()
        if find_article_by_link is not None:
            # db.execute(
            #     'UPDATE off_account_article'
            #     ' SET updated_at = ?'
            #     ' WHERE link = ?',
            #     (current_updated_at, current_link)
            # )
            continue

        ## insert the new article to DB
        # current_app.logger.info(f"{current_article_title} inserted")
        db.execute(
            'INSERT INTO off_account_article (off_account_name, title, updated_at, content, link, registered_at)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (current_off_account_name, current_article_title, current_updated_at, current_content, current_link, current_registered_at)
        )
    db.commit()
    return True


@bp.route('/sync', methods=["GET", "POST"])
@login_required
def sync():
    if request.method == 'POST':
        file = request.files.get("upload-file")
        # check filename
        if file and allowed_file(file.filename):
            # save file
            file_extension = file.filename.rsplit('.', 1)[1]
            saved_filename = f"data_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            saved_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(saved_filepath)
            # process uploaded file
            flash(file.filename + " uploaded successfully!")
            flash("Now synchronizing uploaded file ...")
            if sync_file_to_db(saved_filepath):
                flash("Data synchronized successfully.")
                ## delete archive file
                if current_app.config["DELETE_AFTER_SYNC"]:
                    os.remove(saved_filepath)
                flash("Uploaded file removed.")
        else:
            # wrong file
            flash(f"{file.filename} not allowed")

    ## list all off_account with syncing status

    off_accounts = get_db().execute(
        'SELECT * FROM off_account_list ORDER BY article_updated_at DESC')

    return render_template('admin/sync.html', off_accounts=off_accounts)






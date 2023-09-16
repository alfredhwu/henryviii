"""
package henryviii.model.off_account_follow

this defines the operation for follow / unfollow off_account
"""

from flask import current_app
from henryviii.db import get_db

from datetime import datetime

def get_all_off_account_followed_by_user(username):
    """
    :username: user
    :return: a dict of (off_account_id:off_account_name) of all off_account followed by user
    """
    db = get_db()
    dict_off_accounts = {}
    for r in db.execute(
        'SELECT off_account_id, off_account_name'
        ' FROM off_account_user_meta'
        ' WHERE username= ?'
        ' AND followed_at NOT NULL',
        (username,)
        ).fetchall():
        dict_off_accounts[r["off_account_id"]] = r["off_account_name"]
    return dict_off_accounts

def follow_off_account(off_account_name, off_account_id, username):
    """
    follow the off_account
    :off_account_name: name of off_account to follow
    :off_account_id: id of off_account to follow
    :username: username of whom that wants to follow the off_account
    :return: True of None
    """
    db = get_db()
    db.execute(
        'INSERT OR IGNORE INTO off_account_user_meta (off_account_name, off_account_id, username)'
        ' VALUES (?, ?, ?)',
        (off_account_name, off_account_id, username))
    db.execute(
        'UPDATE off_account_user_meta'
        ' SET followed_at = ?'
        ' WHERE off_account_name = ?'
        ' AND username = ?',
        (datetime.now().strftime('%Y-%m-%d %X'), off_account_name, username,))
    db.commit()

    return True

def unfollow_off_account_by_name(off_account_name, username, drop_related_meta_info=True):
    return unfollow_off_account_by_name_or_id(off_account_name, None, username, drop_related_meta_info)

def unfollow_off_account_by_id(off_account_id, username, drop_related_meta_info=True):
    return unfollow_off_account_by_name_or_id(None, off_account_id, drop_related_meta_info)


def unfollow_off_account_by_name_or_id(off_account_name, off_account_id, username, drop_related_meta_info):
    """
    unfollow the off_account for user identified by username
    :off_account_name
    :off_account_id
    :username
    :drop_related_meta_info: DROP all meta info identified by (off_account_name, username) if True
    """
    db = get_db()
    if drop_related_meta_info:
        db.execute(
            'DELETE FROM off_account_user_meta'
            ' WHERE (off_account_name = ?'
            ' OR off_account_id = ?)'
            ' AND username = ?',
            (off_account_name, off_account_id, username))
    else:
        db.execute(
            'UPDATE off_account_user_meta'
            ' SET followed_at = NULL'
            ' WHERE (off_account_name = ?'
            ' OR off_account_id = ?)'
            ' AND username = ?'
            (off_account_name, off_account_id, username))

    db.commit()
    return True
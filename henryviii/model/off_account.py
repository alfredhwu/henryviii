"""
package henryviii.model.off_account

this defines the operation for off_account
"""

from henryviii.db import get_db

def get_all_off_account():
    """
    :return: dict of off_account_id -> off_account_name
    """
    db = get_db()
    dict_off_accounts = {}
    for r in db.execute(
        'SELECT id, name'
        ' FROM off_account_list'
        ).fetchall():
        dict_off_accounts[r["id"]] = r["name"]
    return dict_off_accounts

def get_off_account_sync_list():    
    """
    :return: dict of off_account_id -> off_account_name
    """
    db = get_db()
    off_account_list = []
    for r in db.execute(
        'SELECT *'
        ' FROM off_account_list'
        ' WHERE update_to_date'
        ).fetchall():
        off_account = {}
        for key in ["name", "category", "article_updated_at", "last_updated_article", "registered_at"]:
            off_account[key] = r[key] 
        off_account_list.append(off_account)
    return off_account_list
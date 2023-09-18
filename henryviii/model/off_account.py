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

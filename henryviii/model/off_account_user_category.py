"""
package henryviii.model.off_account_user_category

this defines the operation for user defined off_account categories
"""
from flask import current_app
from henryviii.db import get_db


"""
CRUD for user_category
"""

def create_user_category(username):
	"""
	"""
	pass

def get_user_categories(username):
	"""
	Get a list of all user defined categories.

	:param username: of whose user defined categories to be retrieved
	:return: list of user defined categories for user identified by param username
	# related table: user_meta
	"""
	db = get_db()
	r_user_category = db.execute(
        'SELECT meta_info'
        ' FROM user_meta'
        ' WHERE username= ?'
        ' AND meta_key= ?',
        (username, "user_category")
        ).fetchone()
	if not r_user_category:
		return []
	return r_user_category["meta_info"].strip().split('|')

def update_user_category(username, from_category, to_category):
	"""
	"""
	pass

def delete_user_category(username, category_name):
	"""
	"""
	pass


"""
Manage the relationship between user_category and off_account

Getter/Setter of user_category for a given off_account

"""

def get_user_category_by_off_account_id(username, off_account_id):
	"""
	"""
	db = get_db()
	r_user_category = db.execute(
		'SELECT user_category'
		' FROM off_account_user_meta'
		' WHERE username = ?'
		' AND off_account_id = ?',
		(username, off_account_id)
		).fetchone()
	if not r_user_category or not r_user_category["user_category"]:
		return None
	return r_user_category["user_category"]

def set_user_category_for_off_account_id(username, off_account_id, new_user_category):
	"""
	"""
	if new_user_category not in get_user_categories(username):
		current_app.logger.error(f"[{ new_user_category }] not in user defined categories.")
		return False
	db = get_db()
	db.execute(
		'UPDATE off_account_user_meta'
		' SET user_category = ?'
		' WHERE username = ?'
		' AND off_account_id = ?',
		(new_user_category, username, off_account_id))
	db.commit()
	return True

def get_all_user_category_by_off_account(username):
	"""
	"""
	db = get_db()
	user_category_list = []
	for r_user_category in db.execute(
		'SELECT off_account_name, off_account_id, user_category'
		' FROM off_account_user_meta'
		' WHERE username = ?'
		' AND followed_at NOT NULL' # if NULL, user might have unfollowed this off_account
		' ORDER BY off_account_name', 
		(username,)):
		user_category_list.append((
			r_user_category["off_account_name"], 
			r_user_category["off_account_id"],
			r_user_category["user_category"]))
	return user_category_list
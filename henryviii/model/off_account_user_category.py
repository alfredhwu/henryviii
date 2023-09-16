"""
package henryviii.model.off_account_user_category

this defines the operation for user defined off_account categories
Getter/Setter of user_category for a given off_account
"""
from flask import current_app
from henryviii.db import get_db
from henryviii.model import user_category as model_user_category


def get_user_category_by_off_account_id(username, off_account_id):
	"""
	Find the user_category assigned to off_account identified by off_account_id

	:param username: name for the user
	:param off_account_id: id of the off_account whose user_category we want
	:return user_cateogry if succeed, None otherwise
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
	Assign the user_category to off_account

	:param username: name for user
	:param off_account_id: id the off_account to whom we want to assign the new user_category
	:param new_user_category: name of the new category
	:return True if succeed
	"""
	if new_user_category not in model_user_category.get_user_categories(username):
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

def get_all_user_category_of_user_following_off_account(username):
	"""
	Get a list of all user followed off_accounts with user_category

	:param username: name for the user
	:return: list of (off_account_name, off_account_id, user_category)
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

def get_dict_of_user_category_with_following_off_account(username):
	"""
	Get a dict of user_category with corresponding followed off_account

	:param username: name for the user
	:return: dict of { user_category : [ (off_account_id, off_account_name) ] }
	with "__default__" reserved for NULL category (not yet assigned by user)
	"""
	user_category_off_account_dict = {}
	default_user_category_off_account = []
	for off_account_name, off_account_id, user_category in get_all_user_category_of_user_following_off_account(username):
		if user_category:
			if user_category in user_category_off_account_dict:
				user_category_off_account_dict[user_category].append((off_account_id, off_account_name))
			else:
				user_category_off_account_dict[user_category] = [(off_account_id, off_account_name)]
		else:
			default_user_category_off_account.append((off_account_id, off_account_name))
	# add other category without off_account
	for user_category in model_user_category.get_user_categories(username):
		if user_category not in user_category_off_account_dict:
			user_category_off_account_dict[user_category] = []
	# add default category
	user_category_off_account_dict[model_user_category.__DEFAULT_USER_CATEGORY__] = default_user_category_off_account
	
	return user_category_off_account_dict



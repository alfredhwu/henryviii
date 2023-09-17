"""
package henryviii.model.user_category

this defines the operation for user defined off_account categories
in a CRUD style
"""
from flask import current_app
from henryviii.db import get_db

__DEFAULT_USER_CATEGORY__ = "__default__"
__META_KEY_FOR_USER_CATEGORY__ = "user_category"

def get_user_category_list_from_string(user_category_string):
	user_category_list =[]
	for user_category in user_category_string.split('|'):
		ucs = user_category.strip()
		if len(ucs) > 0:
			user_category_list.append(ucs)
	return user_category_list

def get_user_category_string_from_list(user_category_list):
	return "" if user_category_list is None else '|'.join(user_category_list)


def create_or_update_user_meta_for_user_category(username, new_user_category_list):
	db = get_db()
	# first guarantee their exist meta_key for user_category
	if len(new_user_category_list) == 0:
		return None
	db.execute(
		'INSERT OR IGNORE INTO user_meta (username, meta_key, meta_info)'
		' VALUES (?, ?, "")',
		(username, __META_KEY_FOR_USER_CATEGORY__))
	# then update the record with new user_category list
	db.execute(
		'UPDATE user_meta'
		' SET meta_info = ?'
		' WHERE username = ? and meta_key = ?',
		('|'.join(new_user_category_list), username, __META_KEY_FOR_USER_CATEGORY__))
	db.commit()
	return True

def add_user_category(username, user_category):
	"""
	Add a new user_category

	:param username: username for user
	:return
	"""
	new_user_category = user_category.strip()
	current_user_category_list = get_user_categories(username)

	# current_app.logger.debug("new user_category:" + new_user_category)
	# current_app.logger.debug(current_user_category_list)
	
	if len(new_user_category) == 0 or new_user_category in current_user_category_list:
		return False
	current_user_category_list.append(new_user_category)
	## flush into the database
	return create_or_update_user_meta_for_user_category(username, current_user_category_list)

def get_user_categories(username):
	"""
	Get a list of all user defined categories.

	:param username: of whose user defined categories to be retrieved
	:return: list of user defined categories for user identified by param username
	# related table: user_meta
	"""
	db = get_db()
	user_category_list =[]
	r_user_category = db.execute(
        'SELECT meta_info'
        ' FROM user_meta'
        ' WHERE username= ?'
        ' AND meta_key= ?',
        (username, __META_KEY_FOR_USER_CATEGORY__)
        ).fetchone()
	if not r_user_category:
		return []
	for user_category in r_user_category["meta_info"].split('|'):
		normalized_user_category = user_category.strip()
		if len(normalized_user_category) == 0:
			continue
		user_category_list.append(normalized_user_category)
	return user_category_list

def update_user_category(username, from_category, to_category):
	"""
	Update a user_category

	:param username: username for user
	:param from_category: old category
	:param to_category: new category
	"""
	pass

def delete_user_category(username, user_category_tobe_delete):
	"""
	Delete a user_category

	:param username: username for user
	:param category_name: category to be removed
	"""
	# first check if user_category_tobe_delete in user_category_list
	user_category_list = get_user_categories(username)
	if user_category_tobe_delete in user_category_list:
		db = get_db()
		## delete all association (off_account --> user_category)
		db.execute(
			'UPDATE off_account_user_meta'
			' SET user_category = NULL'
			' WHERE username = ? and user_category = ?',
			(username, user_category_tobe_delete))
		## delete user_category from list
		user_category_list.remove(user_category_tobe_delete)
		db.execute(
			'UPDATE user_meta'
			' SET meta_info = ?'
			' WHERE username = ? and meta_key = ?',
			('|'.join(user_category_list), username, __META_KEY_FOR_USER_CATEGORY__))
		db.commit()
		return True
	pass
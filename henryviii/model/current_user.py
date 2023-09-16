"""
package henryviii.model.current_user

this defines the operation for current user
"""
from flask import session
from henryviii.db import get_db

def get_current_user():
	"""
	:return: current user
	"""
	user_id = session.get('user_id')

	if user_id is None:
		return None

	return get_db().execute(
		'SELECT * FROM user WHERE id = ?', (user_id,)
		).fetchone()

def get_username():
	current_user = get_current_user()
	return current_user["username"] if current_user else None
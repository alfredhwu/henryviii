"""
package henryviii.model.filter

this defines the operation for filters
"""

from flask import current_app

from henryviii.model import user_category as model_user_category

from datetime import datetime, timedelta


## filter view status
## default all (0), means no view filter
__STATUS_ALL__ = 0
__STATUS_VIEWED__ = 1
__STATUS_NOT_VIEWED__ = 2

## filter favorite
## default all (0), means no favorite filter
__STATUS_FAVORITE__ = 1
__STATUS_NOT_FAVORITE__ = 2

## filter archive
## default all (0), menas no archive filter
__STATUS_ARCHIVED__ = 1
__STATUS_NOT_ARCHIVED__ = 2

def parse(filter_key, filter_arg):
	match filter_key:
		case "user_category":
			return get_filter_user_category(filter_arg)
		case "favorite_status":
			return filter_arg if filter_arg == __STATUS_FAVORITE__ or filter_arg == __STATUS_NOT_FAVORITE__ else __STATUS_ALL__
		case "archive_status":
			return filter_arg if filter_arg == __STATUS_ARCHIVED__ or filter_arg == __STATUS_NOT_ARCHIVED__ else __STATUS_ALL__
		case "view_status":
			return filter_arg if filter_arg == __STATUS_VIEWED__ or filter_arg == __STATUS_NOT_VIEWED__ else __STATUS_ALL__
		case "date_from":
			return get_filter_date_from(filter_arg)
		case "date_to":
			return get_filter_date_to(filter_arg)
	return None


## filter user_category
## default all (None), means no category filter
def get_filter_user_category(user_category):
	"""
	:param user_category: user_category string
	:return: parsed list of user_category
	"""
	user_category_list = model_user_category.get_user_category_list_from_string(user_category)
	return user_category_list if len(user_category_list) > 0 else None

## filter date
def get_filter_date_from(date_str, days_ago=7):
	"""
	Get the normalized date_from from date_str
	:param date_str: 20230915
	:last_days: if date_str is None or blanc, return datetime_str from last_days ago, by default (-1) means 24 hr from now
	:return datetime_str: 2023-09-15 00:00:00
	"""
	try:
		dt = datetime.strptime(date_str, "%Y-%m-%d")
		dt = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
	except:
		dt = datetime.now() - timedelta(days=days_ago)## if parse error, return last 24h
	finally:
		return dt


def get_filter_date_to(date_str):
	"""
	Get the normalized date_to from date_str
	:param date_str: 20230915
	:return datetime_str: 2023-09-15 23:59:59
	if date_str None or blanc, return today
	"""
	# ignore the hh:mm:ss, filter till the end of the day
	try:
		dt = datetime.strptime(date_str, "%Y-%m-%d")
	except:
		dt = datetime.now()
	finally:
		return datetime(dt.year, dt.month, dt.day, 23, 59, 59)


from flask import (
    Blueprint, g, session, request, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.model import current_user, user_category as model_user_category

bp = Blueprint('user_category', __name__)

# @bp.before_app_request
# def load_logged_in_user():
#     g.user = current_user.get_current_user()

"""
Below is the api part of the controller
return JSON object instead of rendering page

"""

@bp.route('/service/')
@login_required
def user_category_index_service():
    """
    list all current user's user category

    :return: JSON of result, with status indicating success or fail
    """
    user_category_list = model_user_category.get_user_categories(current_user.get_username())
    return {
        "status": "success",
        "data": user_category_list
    }

@bp.route('/service/add', methods=['POST'])
@login_required
def user_category_add_service():
    """
    :param from JSON: new user_category
    :return: JSON of result, with status indicating success or fail
    """
    if request.method == 'POST':
        ## retrieve from request data the new_user_category
        new_user_category = request.get_json()["user_category"].strip().replace('|', '_')
        ## check the user_category satified name convensions
        if model_user_category.__DEFAULT_USER_CATEGORY__ == new_user_category:
            return {
                "status": "failure",
                "data": f"User category cannot be named as { model_user_category.__DEFAULT_USER_CATEGORY__ }."
            }
        if not model_user_category.add_user_category(current_user.get_username(), new_user_category):
            return {
                "status": "failure",
                "data": f"User category cannot be added, please check again."
            }
    return {
        "status": "success",
        "data": f"User category [{ new_user_category }] added successfully."
    }

@bp.route('/service/delete', methods=['POST'])
@login_required
def user_category_delete_service():
    """
    :param from JSON: user_category_tobe_delete
    :return: JSON of result, with status indicating success or fail
    """
    if request.method == 'POST':
        user_category_tobe_delete = request.get_json()["user_category"].strip().replace('|', '_')
        if not model_user_category.delete_user_category(current_user.get_username(), user_category_tobe_delete):
            return {
                "status": "failure",
                "data": f"User category [{ user_category_tobe_delete }] not deleted. Please check again."
            }
    return {
        "status": "success",
        "data": f"User category [{ user_category_tobe_delete }] deleted successfully"
    }

@bp.route('/service/update', methods=['POST'])
@login_required
def user_category_update_service():
    """
    :param from JSON: current_user_category, new_user_category
    :return: JSON of result, with status indicating success or fail
    """
    return {
        "status": "success",
        "data": ""
    }










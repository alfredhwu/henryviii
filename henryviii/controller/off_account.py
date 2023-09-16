from flask import (
    Blueprint, flash, g, session, request, redirect, render_template, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.model import current_user
from henryviii.model import (
    off_account as model_off_account, 
    off_account_follow as model_off_account_follow, 
    off_account_user_category as model_off_account_user_category, 
    user_category as model_user_category
)

bp = Blueprint('off_account', __name__)

@bp.before_app_request
def load_logged_in_user():
    g.user = current_user.get_current_user()

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index_controller():

    # get dict of all off_account {id: name}
    dict_off_accounts = model_off_account.get_all_off_account()

    # ## retrieve current followed status from db
    followed_off_account_list = model_off_account_follow.get_all_off_account_followed_by_user(g.user["username"]).values()

    if request.method == 'POST':
        for off_account_id, off_account_name in dict_off_accounts.items():
            ## retrieve form info
            if request.form.get(off_account_name) is None and off_account_name in followed_off_account_list:
                ## unfollow the off_account for user
                model_off_account_follow.unfollow_off_account_by_name(off_account_name, g.user["username"])
            if request.form.get(off_account_name) is not None and off_account_name not in followed_off_account_list:
                ## follow the off_account for user
                model_off_account_follow.follow_off_account(off_account_name, off_account_id, g.user["username"])

    return render_template('off_accounts/index.html', 
                            off_accounts=dict_off_accounts.values(), 
                            followed= #need to refresh
                                model_off_account_follow.get_all_off_account_followed_by_user(g.user["username"]).values(), 
                            # user_categories=model_user_category.get_user_categories(g.user["username"]),
                            off_account_user_category_list=
                                model_off_account_user_category.get_all_user_category_of_user_following_off_account(g.user["username"]),
                            user_category_with_off_accounts=
                                model_off_account_user_category.get_dict_of_user_category_with_following_off_account(g.user["username"]))


"""
Below is the api part of the controller
return JSON object instead of rendering page

"""

@bp.route('/<int:id>/user-category', methods=['GET', 'POST'])
@login_required
def off_account_user_category_controller(id):
    off_account_id = id
    if 'POST' == request.method:
        new_user_category = request.get_json()["new_user_category"]
        ## change user_category to new_user_category
        if not model_off_account_user_category.set_user_category_for_off_account_id(
            g.user["username"], 
            off_account_id, 
            request.get_json()["new_user_category"]):
            return {
                "status": "failure",
                "data": f"fail to update user category[{ new_user_category }] for off_account [{ off_account_id }]"
            }
    return {
        "status": "success",
        "data": model_off_account_user_category.get_user_category_by_off_account_id(g.user["username"], off_account_id)
    }










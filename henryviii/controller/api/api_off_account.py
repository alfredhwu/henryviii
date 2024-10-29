from flask import Blueprint, current_app, jsonify
import json

from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    off_account as model
)


bp = Blueprint('api_off_account', __name__)
current_user = "alfredhwu"

@bp.route('/off/account/sync/list', methods=['GET', 'POST'])
def get_off_account_sync_list():
    off_account_sync_list = model.get_off_account_sync_list()
    # articles = model_article.get_all_article_by_user_filter(
    #     current_user,
    #     {},
    #     page_size=50, page=0)
    # # for article in articles:
    # #     current_app.logger.debug(article["link"] + "||" + article["title"])
    # #     return None
    # return jsonify([{ k : article[k] for k in article.keys()} for article in articles])
    return jsonify(off_account_sync_list)

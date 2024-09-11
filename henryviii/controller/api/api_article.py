from flask import Blueprint, current_app, jsonify
import json

from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    article as model_article
)


bp = Blueprint('api_article', __name__)

@bp.route('/articles', methods=['GET'])
def get_articles():
    articles = model_article.get_all_article_by_user_filter(
        'alfredhwu',
        {},
        page_size=50, page=0)
    # for article in articles:
    #     current_app.logger.debug(article["link"] + "||" + article["title"])
    #     return None
    return jsonify([{ k : article[k] for k in article.keys()} for article in articles])

    # return jsonify([
    #     {
    #         "publisher": "a",
    #         "title": "a",
    #     },
    #     {
    #         "publisher": "b",
    #         "title": "b",
    #     },
    #     {
    #         "publisher": "b",
    #         "title": "b",
    #     }
    # ])
from flask import Blueprint, current_app, jsonify
import json

from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    article as model_article
)


bp = Blueprint('api_article', __name__)
current_user = "alfredhwu"

@bp.route('/articles', methods=['GET', 'POST'])
def get_articles():
    articles = model_article.get_all_article_by_user_filter(
        current_user,
        {},
        page_size=50, page=0)
    # for article in articles:
    #     current_app.logger.debug(article["link"] + "||" + article["title"])
    #     return None
    return jsonify([{ k : article[k] for k in article.keys()} for article in articles])

@bp.route('/article/<int:id>/view', methods=['POST'])
def view_article(id):
    ## update view status for article [id]
    if model_article.set_article_viewed_by_id(current_user, id):
        return jsonify({ "status": "success", "message": "successfully viewed the article" })

    return jsonify({ "status": "failure", "message": "oops, something went wrong, failed to view the article"})


@bp.route('/article/<int:id>/like/cancel', methods=['POST'])
def cancel_like_article(id): 
    if model_article.set_article_liked_by_id(current_user, id, False):
        return jsonify({ "status": "success", "message": "successfully cancel the liked status for the article" })
    return jsonify({ "status": "failure", "message": "oops, something went wrong, failed to cancel the liked status for the article"})


@bp.route('/article/<int:id>/like', methods=['POST'])
def like_article(id):
    if model_article.set_article_liked_by_id(current_user, id):
        return jsonify({ "status": "success", "message": "successfully liked the article" })
    return jsonify({ "status": "failure", "message": "oops, something went wrong, failed to like the article"})


# @bp.route('/article/<int:id>/dislike', methods=['POST'])
# @login_required
# def dislike(id):
#     pass


# @bp.route('/article/<int:id>/dislike/cancel', methods=['POST'])
# @login_required
# def cancel_dislike(id):
#     pass


@bp.route('/article/<int:id>/delete', methods=['POST'])
def delete(id):
    if model_article.set_article_deleted_by_id(current_user, id):
        return jsonify({ "status": "success", "message": "successfully deleted the article" })

    return jsonify({ "status": "failure", "message": "oops, something went wrong, failed to delete the article"})


from flask import (
    Blueprint, flash, g, session, request, redirect, render_template, url_for
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required

bp = Blueprint('account', __name__)

@bp.route('/')
@login_required
def account_controller():
    return render_template('account/index.html')


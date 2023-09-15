from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort

from henryviii.controller.auth import login_required
from henryviii.db import get_db

# import xlrd
from openpyxl import Workbook, load_workbook
import pandas as pd
from datetime import date, datetime

bp = Blueprint('account', __name__)

@bp.route('/')
@login_required
def account():
    return render_template('account/index.html')


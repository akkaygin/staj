from flask import Blueprint, render_template, session, request, url_for
from math import ceil

from .. import db

DEFAULT_EPP = 10
DEFAULT_SORT = 'id'

bp = Blueprint('dashboard', __name__)

def make_url(page, epp):
  return url_for('dashboard.dashboard',page=page, epp=None if epp == DEFAULT_EPP else epp)

@bp.get('/dashboard')
def dashboard():
  if 'email' not in session:
    return render_template('dashboard.html', users=None, email=None)
  
  epp = request.args.get('epp', DEFAULT_EPP, int)
  page = request.args.get('page', 1, int)
  sort = request.args.get('sort', 'id')
  dir = request.args.get('dir', 'asc')

  user_count = db.get_user_count()
  n_pages = max(ceil(user_count / epp), 1)
  page = min(page, n_pages)
  user_list = db.get_user_list(page - 1, epp, sort, dir)

  pagination_lut = {
    'page': page,
    'n_pages': n_pages,
    'epp': epp,
    'pec': len(user_list),
    
    'np_hl': make_url(page + 1, epp),
    'pp_hl': make_url(page - 1, epp),

    'epps': [10, 30, 50],
  }
  
  return render_template('dashboard.html', users=user_list,\
                         email=session['email'], plut=pagination_lut,
                         sort=sort, dir=dir, query=request.args)
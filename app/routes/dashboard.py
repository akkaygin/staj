from flask import Blueprint, render_template, session, request, url_for

from ..db import user_db

DEFAULT_EPP = 10

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard():
  if 'email' not in session:
    return render_template('dashboard.html.jinja', users=None, email=None)
  
  '''
    epp/pagination works but i cannot preserve more than one
    argument per link-click so entries per page is useless unless
    i precompute urls for every hyperlink modifying arguments
  '''
  epp = request.args.get('epp', DEFAULT_EPP, int)
  page = request.args.get('page', 1, int)

  '''
    user_db is not guaranteed to be ordered,
    but this should be fine for now
  '''
  start = (page - 1) * epp
  user_list = list(user_db.values())[start:start + epp]
  
  return render_template('dashboard.html.jinja', users=user_list,\
                         email=session['email'], page=page,\
                         epp=epp, total_pages=len(user_db.values())//epp+1)
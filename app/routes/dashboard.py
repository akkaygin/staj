from flask import Blueprint, render_template, session, request, url_for

from ..db import user_db

DEFAULT_EPP = 4

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard():
  if 'email' not in session:
    return render_template('dashboard.html.jinja', users=None, email=None)
  
  epp = request.args.get('epp', DEFAULT_EPP, int)
  page = request.args.get('page', 1, int)

  '''
    user_db is not guaranteed to be ordered,
    but this should be fine for now
  '''
  start = (page - 1) * epp
  user_list = list(user_db.values())[start:start + epp]

  pagination_lut = {
    'page': page,
    'n_pages': len(user_db.values())//epp+1,
    'epp': epp,
    'pec': len(user_list),
    
    'np_hl': url_for('dashboard.dashboard', page=page+1, epp=None if epp == DEFAULT_EPP else epp),
    'pp_hl': url_for('dashboard.dashboard', page=page-1, epp=None if epp == DEFAULT_EPP else epp),
  }
  
  return render_template('dashboard.html.jinja', users=user_list,\
                         email=session['email'], plut=pagination_lut)
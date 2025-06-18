from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from ... import db

bp = Blueprint('confirm', __name__)

@bp.route('/auth/confirm', methods=['GET', 'POST'])
def confirm():
  if not current_user.is_authenticated:
    return redirect(url_for('login.login'))
  
  if current_user.is_confirmed:
    return redirect(url_for('dashboard.dashboard'))
  
  if db.is_confirmation_expired(current_user.email):
    flash('Code has timed out', 'error')
    return redirect(url_for('confirm.resend'))
  
  if request.method == 'POST':
    code = None
    if request.args.get('code') is not None:
      code = request.args.get('code')
    else:
      code = request.form['code']
    
    if db.confirm_user({'email': current_user.email, 'code': code}):
      return redirect(url_for('dashboard.dashboard'))
    
    flash('Invalid code', 'error')
    
  return render_template('confirm.html', email=current_user.email)

@bp.get('/auth/resend')
def resend():
  if not current_user.is_authenticated:
    return redirect(url_for('login.login'))
  
  if current_user.is_confirmed:
    return redirect(url_for('dashboard.dashboard'))
  
  db.resend_confirmation(current_user.email)
  flash('Confirmation E-Mail sent', 'success')
  return redirect(url_for('confirm.confirm'))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ... import db

bp = Blueprint('confirm', __name__)

@bp.get('/auth/confirm')
def confirm():
  error = None
  email = request.args.get('email')
  if email is None:
    error = 'An E-Mail address is required for confirmation'
    flash(error, 'error')
    return redirect(url_for('login.login'))
  
  if db.is_user_confirmed(email):
    flash('E-Mail already confirmed', 'error')
    return redirect(url_for('login.login'))

  return render_template('confirm.html.jinja', email=email)

@bp.post('/auth/confirm')
def confirm_post():
  error = None
  email = request.args.get('email')
  if email is None:
    error = 'An E-Mail address is required for confirmation'
    flash(error, 'error')
    return redirect(url_for('login.login'))
  
  if db.is_user_confirmed(email):
    flash('E-Mail already confirmed', 'error')
    return redirect(url_for('login.login'))
  
  error = db.confirm_user({
    'email': email,
    'code': request.form['code'],
  })
  if error is None:
    session['email'] = email
    return redirect(url_for('dashboard.dashboard'))
  
  if error == 'Code has timed out':
    flash(error, 'error')
    return redirect(url_for('confirm.resend', email=email))

@bp.get('/auth/resend')
def resend():
  email = request.args.get('email')
  if email is None:
    return redirect(url_for('confirm.confirm', email=None))
  
  if db.is_user_confirmed(email):
    flash('E-Mail already confirmed', 'error')
    return redirect(url_for('login.login'))
  
  error = db.resend_confirmation(email)
  if error is None:
    flash('Confirmation E-Mail sent', 'success')
    return redirect(url_for('confirm.confirm', email=email))

  flash(error, 'error')
  return redirect(url_for('login.login'))
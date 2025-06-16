from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ... import db

bp = Blueprint('confirm', __name__)

@bp.route('/auth/confirm', methods=['GET', 'POST'])
def confirm():
  email = request.args.get('email')
  if email is None:
    flash('An E-Mail address is required for confirmation', 'error')
    return redirect(url_for('login.login'))
  
  if db.is_user_confirmed(email):
    flash('E-Mail already confirmed', 'error')
    return redirect(url_for('login.login'))

  if request.method == 'POST':
    code = request.form['code']
    if code is None:
      flash('Confirmation code is missing', 'error')
      return redirect(url_for('confirm.confirm', email=email))
    
    error = db.confirm_user({'email': email, 'code': code})
    if error == 'Code has timed out':
      flash('Code has timed out', 'error')
      return redirect(url_for('confirm.resend', email=email))
    elif error == 'Invalid confirmation code':
      flash('Invalid confirmation code', 'error')
    else:
      session['email'] = email
      return redirect(url_for('dashboard.dashboard'))
  
  return render_template('confirm.html', email=email)

@bp.route('/auth/resend', methods=['GET', 'POST'])
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
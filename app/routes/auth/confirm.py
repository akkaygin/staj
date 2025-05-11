from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ... import db

bp = Blueprint('confirm', __name__)

@bp.route('/auth/confirm', methods=['GET', 'POST'])
def confirm():
  error = None
  email = request.args.get('email')
  if email is None:
    error = 'An E-Mail address is required for confirmation'
    flash(error, 'error')
    return redirect(url_for('login.login'))

  if request.method == 'POST':  
    if error is None:
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
    
    if error == 'E-Mail already confirmed':
      return redirect(url_for('login.login', email=email))

    flash(error, 'error')
  
  return render_template('confirm.html.jinja', email=email)

@bp.route('/auth/resend', methods=['GET', 'POST'])
def resend():
  error = None
  email = request.args.get('email')
  if email is None:
    error = ''
  
  if error is None:
    error = db.resend_confirmation(email)
  
  if error is None:
    flash('Confirmation E-Mail sent', 'success')
    return redirect(url_for('confirm.confirm', email=email))

  return redirect(url_for('confirm.confirm', email=email))
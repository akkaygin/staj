from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re

from ... import db

bp = Blueprint('login', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return None
  
  return 'Enter a valid E-Mail address'
  
@bp.route('/auth/login', methods=['GET', 'POST'])
def login():
  if 'email' in session:
    return redirect(url_for('dashboard.dashboard'))

  if request.method == 'POST':
    error = None
    if not request.form['email']:
      error = 'An email address is required'
    elif not request.form['password']:
      error = 'A password is required'

    error = is_email_valid(request.form['email'])
    if error is not None:
      flash(error, 'error')
      return render_template('register.html.jinja')

    if error is None:
      error = db.check_credentials({
        'email': request.form['email'],
        'password': request.form['password'],
      })

    if error is None:
      session['email'] = request.form['email']
      return redirect(url_for('dashboard.dashboard'))
    
    if error == 'E-Mail not confirmed':
      flash(error, 'error')
      return redirect(url_for('confirm.confirm', email=request.form['email']))
    
    flash(error, 'error')
  
  return render_template('login.html.jinja')

@bp.route('/auth/logout')
def logout():
  session.pop('email', None)
  flash('Logged out', 'success')
  return redirect(url_for('login.login'))
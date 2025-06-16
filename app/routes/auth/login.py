from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re

from ... import db

bp = Blueprint('login', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return True
  
  return False
  
@bp.route('/auth/login', methods=['GET', 'POST'])
def login():
  if 'email' in session:
    return redirect(url_for('dashboard.dashboard'))

  if request.method == 'POST':
    if request.form['email'] is None:
      flash('An email address is required', 'error')
      return render_template('login.html')
    
    if request.form['password'] is None:
      flash('A password is required', 'error')
      return render_template('login.html')

    if not is_email_valid(request.form['email']):
      flash('Enter a valid E-Mail address', 'error')
      return render_template('register.html')
    
    error = db.check_credentials({'email': request.form['email'], 'password': request.form['password']})
    if error == 'E-Mail not confirmed':
      flash(error, 'error')
      return redirect(url_for('confirm.confirm', email=request.form['email']))
    elif error is not None:
      flash(error, 'error')
      return render_template('login.html')
    else:
      session['email'] = request.form['email']
      return redirect(url_for('dashboard.dashboard'))
  
  return render_template('login.html')

@bp.route('/auth/logout')
def logout():
  session.pop('email', None)
  flash('Logged out', 'success')
  return redirect(url_for('login.login'))
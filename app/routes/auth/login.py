from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re

from ... import db

bp = Blueprint('login', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return True
  return False
  
@bp.get('/auth/login')
def login():
  if 'email' in session:
    return redirect(url_for('dashboard.dashboard'))
  
  return render_template('login.html')

@bp.post('/auth/login')
def login_post():
  if not request.form['email']:
    flash('An email address is required', 'error')
    return render_template('register.html')
  elif not request.form['password']:
    flash('A password is required', 'error')
    return render_template('register.html')

  if not is_email_valid(request.form['email']):
    flash('Enter a valid E-Mail address', 'error')
    return render_template('register.html')

  error = db.check_credentials({
    'email': request.form['email'],
    'password': request.form['password'],
  })
  if error is None:
    session['email'] = request.form['email']
    return redirect(url_for('dashboard.dashboard'))
  
  if error == 'User not confirmed':
    flash(error, 'error')
    return redirect(url_for('confirm.confirm', email=request.form['email']))
  
  flash(error, 'error')
  return render_template('login.html')

@bp.get('/auth/logout')
def logout():
  session.pop('email', None)
  flash('Logged out', 'success')
  return redirect(url_for('login.login'))
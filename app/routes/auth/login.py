from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import re

from ... import db

bp = Blueprint('login', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return True
  return False
  
@bp.route('/auth/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    if current_user.is_confirmed:
      return redirect(url_for('dashboard.dashboard'))
    else:
      return redirect(url_for('confirm.confirm'))
  
  if request.method == 'POST':
    if not request.form['email']:
      flash('An email address is required', 'error')
      return render_template('register.html')
    
    if not request.form['password']:
      flash('A password is required', 'error')
      return render_template('register.html')

    if not is_email_valid(request.form['email']):
      flash('Enter a valid E-Mail address', 'error')
      return render_template('register.html')

    user_data = db.check_credentials({
      'email': request.form['email'],
      'password': request.form['password'],
    })
    if user_data is not None:
      login_user(db.User(user_data))
      if not current_user.is_confirmed:
        return redirect(url_for('confirm.confirm'))
      
      return redirect(url_for('dashboard.dashboard'))
    
    flash('Invalid credentials', 'error')
  
  return render_template('login.html')

@bp.route('/auth/logout')
@login_required
def logout():
  logout_user()
  flash('Logged out', 'success')
  return redirect(url_for('login.login'))
from flask import Blueprint, render_template, request, redirect, url_for, flash
import re

from ... import db

bp = Blueprint('register', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return True
  
  return False

def is_phone_number_valid(number):
  if bool(re.fullmatch(r'\+?\d{10,15}', number)):
    return True
  
  return False

def is_password_strong(password):
  if len(password) < 8:
    return 'Password must be longer than 8 characters'

  if len(re.findall(r'[a-z]', password)) == 0:
    return 'Password must contain a lowercase character'
  
  if len(re.findall(r'[A-Z]', password)) == 0:
    return 'Password must contain an uppercase character'
  
  if len(re.findall(r'\d', password)) == 0:
    return 'Password must contain a digit'
  
  if len(re.findall(r'[^A-Za-z\d!@#$%^&*]', password)) != 0:
    return 'Password must not contain any special character except !@#$%^&*'

  return None

def is_address_legal(address):
  if bool(re.findall(r'\|', address)):
    return False

  return True

@bp.route('/auth/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    if not request.form['email']:
      flash('An email address is required', 'error')
      return render_template('register.html')
    
    if not request.form['password']:
      flash('A password is required', 'error')
      return render_template('register.html')
    
    if not request.form['phone']:
      flash('A phone number is required', 'error')
      return render_template('register.html')
    
    if not request.form['address']:
      flash('An address is required', 'error')
      return render_template('register.html')
     
    if not is_email_valid(request.form['email']):
      flash('Enter a valid E-Mail address', 'error')
      return render_template('register.html')
    
    error = is_password_strong(request.form['password'])
    if error is not None:
      flash(error, 'error')
      return render_template('register.html')
    
    if not is_phone_number_valid(request.form['phone']):
      flash('Enter a valid phone number', 'error')
      return render_template('register.html')
    
    if not is_address_legal(request.form['address']):
      flash('Address cannot contain the \'|\' character', 'error')
      return render_template('register.html')
    
    error = db.add_user({
      'email': request.form['email'],
      'password': request.form['password'],
      'phone': request.form['phone'],
      'address': request.form['address'],
    })
    if error is None:
      return redirect(url_for('confirm.confirm', email=request.form['email']))
      
    if error == 'E-Mail registered bu not confirmed':
      flash(error, 'error')
      return redirect(url_for('confirm.confirm', email=request.form['email']))
  
  return render_template('register.html')

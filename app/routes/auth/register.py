from flask import Blueprint, render_template, request, redirect, url_for, flash
import re

from ... import db

bp = Blueprint('register', __name__)

def is_email_valid(email):
  if bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
    return None
  
  return 'Enter a valid E-Mail address'

def is_phone_number_valid(number):
  if bool(re.fullmatch(r'\+?\d{10,15}', number)):
    return None
  
  return 'Enter a valid phone number'

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
    return 'Address cannot contain the \'|\' character'

  return None

@bp.get('/auth/register')
def register():
  return render_template('register.html.jinja')

@bp.post('/auth/register')
def register_post():
  error = None
  if not request.form['email']:
    error = 'An email address is required'
  elif not request.form['password']:
    error = 'A password is required'
  elif not request.form['phone']:
    error = 'A phone number is required'
  elif not request.form['address']:
    error = 'An address is required'

  if error is not None:
    flash(error, 'error')
    return render_template('register.html.jinja')

  error = is_email_valid(request.form['email'])
  if error is not None:
    flash(error, 'error')
    return render_template('register.html.jinja')
  
  error = is_password_strong(request.form['password'])
  if error is not None:
    flash(error, 'error')
    return render_template('register.html.jinja')
  
  error = is_phone_number_valid(request.form['phone'])
  if error is not None:
    flash(error, 'error')
    return render_template('register.html.jinja')
  
  error = is_address_legal(request.form['address'])
  if error is not None:
    flash(error, 'error')
    return render_template('register.html.jinja')
  
  if error is None:
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

  flash(error, 'error')
from hashlib import pbkdf2_hmac
from secrets import token_hex
import csv
from time import time

DB_FILE = 'db.csv'
HASH_ITERATIONS = 1 # would use 600000 in production
FIELDNAMES = [
  'email',
  'salt',
  'hash',
  'phone',
  'address',
  'code',
  'code_ts'
]

CODE_TIMEOUT = 1800 # 30 minutes

user_db = {}

def check_n_create():
  try:
    with open('db.csv', 'x') as _:
      pass
  except FileExistsError:
    pass

def read_db():
  check_n_create()
  with open('db.csv', 'r', newline='') as dbf:
    reader = csv.DictReader(dbf, quotechar='|')
    for user in reader:
      user_db[user['email']] = user

def write_db():
  with open('db.csv', 'w', newline='') as dbf:
    writer = csv.DictWriter(dbf, quotechar='|', fieldnames=FIELDNAMES)
    writer.writeheader()
    for _, row in user_db.items():
      writer.writerow(row)

def add_user(data):
  if data['email'] in user_db:
    if user_db[data['email']]['code'] != 'confirmed':
      return 'E-Mail registered bu not confirmed'
    
    return 'E-Mail address already registered'
  
  salt = token_hex(16)
  dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(salt, 'utf-8'), HASH_ITERATIONS).hex()
  
  confirmation_code = token_hex(2)
  print(f'E-Mail confirmation code: {confirmation_code}')

  user_db[data['email']] = {
    'email': data['email'],
    'salt': str(salt),
    'hash': dk,
    'phone': data['phone'],
    'address': data['address'],
    'code': confirmation_code,
    'code_ts': int(time())
  }

  write_db()

  return None

def confirm_user(data):
  if data['email'] not in user_db:
    return 'No such E-Mail'
  
  user = user_db[data['email']]

  if user['code'] == 'confirmed':
    return 'E-Mail already confirmed'
  
  if user['code'] != data['code']:
    return 'Invalid confirmation code'
  
  if int(time()) - int(user['code_ts']) > CODE_TIMEOUT:
    return 'Code has timed out'
  
  user_db[data['email']]['code'] = 'confirmed'

  write_db()
  
  return None

def resend_confirmation(email):
  if email not in user_db:
    return 'No such E-Mail'

  if user_db[email]['code'] == 'confirmed':
    return 'Confirmation not necessary'
  
  confirmation_code = token_hex(2)
  print(f'E-Mail confirmation code: {confirmation_code}')
  user_db[email]['code'] = confirmation_code

  write_db()

  return None

def check_credentials(data):
  '''
    this can be converted to an 'invalid credential'
    to anonymize email addresses
  '''
  if data['email'] not in user_db:
    return 'Invalid E-Mail address'
  
  user = user_db[data['email']]
  dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(user['salt'], 'utf-8'), HASH_ITERATIONS).hex()
  if dk != user['hash']:
    return 'Invalid password'
  
  if user['code'] != 'confirmed':
    return 'E-Mail not confirmed'
  
  return None
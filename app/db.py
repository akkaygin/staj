from hashlib import pbkdf2_hmac
from secrets import token_hex
import sqlite3
from datetime import datetime, timedelta

DB_FILE = 'database.db'
HASH_ITERATIONS = 1 # would use 600000 in production

CODE_TIMEOUT = 1800 # 30 minutes

def init_db():
  with sqlite3.connect(DB_FILE) as db:
    cursor = db.cursor()
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

        password TEXT NOT NULL,
        salt TEXT NOT NULL,
        
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,

        is_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
        confirmation_code TEXT,
        confirmation_expiry TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    ''')
    db.commit()

def create_confirmation_code():
  return token_hex(2)

def add_user(data):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    if query_result is not None:
      if query_result["is_confirmed"] is True:
        return 'User registered but not confirmed'
      return 'User already registered'

    salt = token_hex(16)
    dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(salt, 'utf-8'), HASH_ITERATIONS).hex()
  
    confirmation_code = create_confirmation_code()
    print(f'E-Mail confirmation code: {confirmation_code}')

    values = (dk, salt, data['email'], data['address'], data['phone'], confirmation_code, datetime.now() + timedelta(minutes=CODE_TIMEOUT))
    cursor.execute('INSERT INTO users (password, salt, email, address, phone, confirmation_code, confirmation_expiry) VALUES (?, ?, ?, ?, ?, ?, ?);', values)
  
  return None

def confirm_user(data):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    if query_result is None:
      return 'User does not exist'
    
    if query_result['is_confirmed'] is True:
      return 'User already confirmed'
      
    if query_result['confirmation_code'] == data['code']:
      if datetime.fromisoformat(query_result[9]) < datetime.now():
        return 'Code has timed out'
        
      cursor.execute('UPDATE users SET is_confirmed = TRUE WHERE email = ?;', (data['email'],))
      db.commit()

  return None

def is_user_confirmed(email):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (email,))
    query_result = cursor.fetchone()
    if query_result is not None:
      return query_result['is_confirmed']
    
    return False

def resend_confirmation(email):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (email,))
    query_result = cursor.fetchone()
    if query_result is None:
      return 'User does not exist'
    
    if query_result['is_confirmed'] is True:
      return 'User already confirmed'
      
    confirmation_code = create_confirmation_code()
    print(f'E-Mail confirmation code: {confirmation_code}')

    confirmation_expiry = datetime.now() + timedelta(minutes=30)

    cursor.execute('UPDATE users SET confirmation_code = ? confirmation_expiry = ? WHERE email = ?;', (confirmation_code, confirmation_expiry, email))
    db.commit()

  return None
  
def check_credentials(data):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    if query_result is None:
      return 'User does not exist'
    
    dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(query_result['salt'], 'utf-8'), HASH_ITERATIONS).hex()
    if data['password'] != dk:
      return 'Invalid password'
      
    if not query_result['is_confirmed']:
      return 'User not confirmed'
      
  return None

SORTABLE_FIELD_NAMES = {'id', 'email', 'created', 'phone', 'address', 'is_confirmed', 'code_expiry'}
def get_user_list(page, epp, sort, dir):
  sort = sort if sort in SORTABLE_FIELD_NAMES else 'id'
  dir = 'DESC' if dir == 'desc' else 'ASC'

  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM users ORDER BY {sort} {dir} LIMIT ? OFFSET ?', (epp, page * epp))
    return [dict(row) for row in cursor.fetchall()]

def get_user_count():
  with sqlite3.connect(DB_FILE) as db:
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM users;')
    result = cursor.fetchone()
    return result[0] if result else 0
from hashlib import pbkdf2_hmac
from secrets import token_hex
import sqlite3
from datetime import datetime, timedelta

from flask_login import LoginManager, UserMixin

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
      return None

    salt = token_hex(16)
    dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(salt, 'utf-8'), HASH_ITERATIONS).hex()
  
    confirmation_code = create_confirmation_code()
    print(f'E-Mail confirmation code: {confirmation_code}')

    values = (dk, salt, data['email'], data['address'], data['phone'], confirmation_code, datetime.now() + timedelta(minutes=CODE_TIMEOUT))
    cursor.execute('INSERT INTO users (password, salt, email, address, phone, confirmation_code, confirmation_expiry) VALUES (?, ?, ?, ?, ?, ?, ?);', values)
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    return query_result

  return None

def is_confirmation_expired(email):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (email,))
    query_result = cursor.fetchone()
    
    if datetime.fromisoformat(query_result['confirmation_expiry']) < datetime.now():
      return True
      
  return False

def confirm_user(data):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    
    if query_result['confirmation_code'] == data['code']:
      if datetime.fromisoformat(query_result['confirmation_expiry']) < datetime.now():
        return False
        
      cursor.execute('UPDATE users SET is_confirmed = TRUE WHERE email = ?;', (data['email'],))
      db.commit()

      return True

  return False

def is_user_confirmed(email):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (email,))
    query_result = cursor.fetchone()
    if query_result is not None:
      return bool(query_result["is_confirmed"])
  
def resend_confirmation(email):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    confirmation_code = create_confirmation_code()
    print(f'E-Mail confirmation code: {confirmation_code}')

    confirmation_expiry = datetime.now() + timedelta(minutes=30)

    cursor.execute('UPDATE users SET confirmation_code = ?, confirmation_expiry = ? WHERE email = ?;', (confirmation_code, confirmation_expiry, email))
    db.commit()
  
def check_credentials(data):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?;', (data['email'],))
    query_result = cursor.fetchone()
    if query_result is None:
      return None
    
    dk = pbkdf2_hmac('sha256', bytes(data['password'], 'utf-8'), bytes(query_result['salt'], 'utf-8'), HASH_ITERATIONS).hex()
    if query_result['password'] != dk:
      return None

    return query_result

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
  
def get_user_info(user_id):
  with sqlite3.connect(DB_FILE) as db:
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?;', (user_id,))
    query_result = cursor.fetchone()
    return query_result

class User(UserMixin):
  def __init__(self, user_data):
    self.id = str(user_data['id'])
    self.created_at = user_data['created']
    self.password = user_data['password']
    self.salt = user_data['salt']
    self.email = user_data['email']
    self.address = user_data['address']
    self.phone = user_data['phone']
    self.is_confirmed = bool(user_data['is_confirmed'])
    self.confirmation_code = user_data['confirmation_code']
    self.confirmation_expiry = user_data['confirmation_expiry']
  
  def get_id(self):
    return self.id

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
  user_data = get_user_info(user_id)
  if user_data is None:
    return None
  
  return User(user_data)
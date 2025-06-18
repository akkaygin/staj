from flask import Flask, redirect, url_for

from . import db

def create_app():
  app = Flask(__name__)
  app.secret_key = 'dev'

  db.init_db()

  from .routes.auth import register
  app.register_blueprint(register.bp)

  from .routes.auth import login
  app.register_blueprint(login.bp)

  from .routes.auth import confirm
  app.register_blueprint(confirm.bp)

  from .routes import dashboard
  app.register_blueprint(dashboard.bp)

  return app

app = create_app()

db.login_manager.init_app(app)
db.login_manager.login_view = 'login.login'
db.login_manager.login_message_category = 'info'

@app.route('/')
def index():
  return redirect(url_for('dashboard.dashboard'))

if __name__ == "__main__":
  app.run()
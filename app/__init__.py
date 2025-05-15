from flask import Flask, redirect, url_for

def create_app():
  app = Flask(__name__)
  app.config.from_mapping(
    SECRET_KEY='dev',
  )

  from . import db
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

@app.route('/')
def index():
  return redirect(url_for('dashboard.dashboard'))

if __name__ == "__main__":
  app.run()
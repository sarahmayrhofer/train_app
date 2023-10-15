from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.routes import main
from config import Config

app = Flask(__name__)
app.register_blueprint(main)

app.config.from_object(Config)

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)

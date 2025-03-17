from flask import Flask
from config import Config
from models import db
from routes.registros import registros_bp
from routes.downloads import downloads_bp


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


with app.app_context():
    db.create_all()


app.register_blueprint(registros_bp)
app.register_blueprint(downloads_bp)

if __name__ == "__main__":
    app.run(debug=True)
app.debug = True 
app.run(debug=True)
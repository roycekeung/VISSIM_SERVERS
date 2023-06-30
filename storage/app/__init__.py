#################################################################################
#
#   Description : init of application bu base is flask
#
#################################################################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from app.config import Config


db = SQLAlchemy()

api = Api(default_mediatype="application/json")




def create_app(config=Config):
    #Flask(__name__, template_folder='templates')  default
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    from app import routes
    api.init_app(app)

    ### --- --- --- for html web visual --- --- --- 
    from flask import render_template
    @app.route('/ping', methods=['GET'])
    def home():
        return render_template("index.html")
    
    return app



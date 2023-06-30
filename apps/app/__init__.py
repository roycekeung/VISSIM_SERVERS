#################################################################################
#
#   Description : init of application bu base is flask
#
#################################################################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from app.config import Config

from computation.cal import RunCal  

import logging
from computation.callog import*

import os

api = Api(default_mediatype="application/json")
#Flask(__name__, template_folder='templates')  default
app = Flask(__name__)
app.config.from_object(Config)


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app import routes
    api.init_app(app)
    
    
    ### --- --- --- for html web visual --- --- --- 
    from flask import render_template
    @app.route('/ping', methods=['GET'])
    def home():
        return render_template("index.html")

    @app.route('/appservinf', methods=['GET'])
    def inf():
        ### status on this applicatiion server end
        jobid = compute.getjobid()
        jobname = compute.getjobname()
        eval = compute.geteval()
        
        runtime = compute.getruntime_informat()
        isrunning = compute.isrunning()
        sleeptime = compute.getsleeptime()

        curresultsnum = compute.getcurresultsnames()
        
        return render_template("appservinf.html", 
                            jobid = jobid, 
                            jobname = jobname,
                            eval= eval, 
                            runtime= runtime,
                            isrunning= isrunning,
                            sleeptime= sleeptime,
                            curresultsnum= curresultsnum
                            ) 

    
    return app



# compute= RunCal(sec = 3, resource_class_kwargs={'logger': logging.getLogger(__name__) })
compute= RunCal(sec = 3)

def get_RunCal():

    return compute
#################################################################################
#
#   Description : all starting configs setting
#
#################################################################################

import os

import urllib

from datetime import timedelta

# database linkage
ACCESS_PARAMS = ('postgresql://postgres:%s@localhost/vissim_db' %  urllib.parse.quote(r'a71m46', safe=''))


# backend
class Config(object):
    # flask
    DEBUG = os.environ.get('FLASK_DEBUG') or False

    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or ACCESS_PARAMS
    SQLALCHEMY_TRACK_MODIFICATIONS = False   ## True
    


# backend server
LOADBAL_SERVER = ["127.0.0.1:5400"]   ## localhost


# QUE server
QUE_SERVER = "127.0.0.1"   ## localhost

# storage server
STORAGE_SERVER = ["127.0.0.1:5500"]  ## localhost

# app server
APP_SERVERS = ["127.0.0.1:5600", '127.0.0.1:5601', '127.0.0.1:5602', '127.0.0.1:5603']   ###...


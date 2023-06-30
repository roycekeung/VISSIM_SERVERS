#################################################################################
#
#   Description : all starting configs setting
#
#################################################################################

import os

from datetime import timedelta

from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(find_dotenv(), verbose=True)

# backend server
LOADBAL_SERVER = os.getenv('LOADBAL_SERVER')    ## localhost 


# QUE server
QUE_SERVER = os.getenv('QUE_SERVER')   ## localhost

# storage server
STORAGE_SERVER = os.getenv('STORAGE_SERVER')   ## localhost



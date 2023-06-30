#################################################################################
#
#   Description : rest API router
#
#################################################################################

import logging.config

import socket
This_hostname = socket.gethostbyname(socket.gethostname())


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)




import redis

# using time module
import time

import requests
  
### total count = 9
# SERVER_POOL = ['127.0.0.1:5600','127.0.0.1:5601','127.0.0.1:5602','127.0.0.1:5603'] ## localhost test
# SERVER_POOL = ['143.89.22.34:5600','143.89.22.34:5601','143.89.22.34:5602','143.89.22.34:5603', \
    # '143.89.22.21:5600','143.89.22.21:5601','143.89.22.21:5602','143.89.22.21:5603', \   ### fyp
    # '143.89.22.131:5600','143.89.22.131:5601','143.89.22.131:5602','143.89.22.131:5603', \   ### Enoch
    # '143.89.247.179:5600','143.89.247.179:5601','1143.89.247.179:5602','143.89.247.179:5603']   ### DISCO

# SERVER_POOL = ['143.89.22.21:5600','143.89.22.21:5601','143.89.22.21:5602','143.89.22.21:5603', \
    # '143.89.22.131:5600','143.89.22.131:5601','143.89.22.131:5602','143.89.22.131:5603', \
    # '143.89.247.179:5600','143.89.247.179:5601','143.89.247.179:5602','143.89.247.179:5603']   ### ### fyp, Enoch, DISCO

SERVER_POOL = ['143.89.22.21:5600','143.89.22.21:5601','143.89.22.21:5602','143.89.22.21:5603', \
    '143.89.22.131:5600','143.89.22.131:5601','143.89.22.131:5602','143.89.22.131:5603']   ### ### fyp, Enoch

## SERVER_POOL = ['143.89.22.34:5600','143.89.22.34:5601','143.89.22.34:5602','143.89.22.34:5603', \
##    '143.89.247.164:5604','143.89.247.164:5605','143.89.247.164:5606','143.89.247.164:5607']


# ts stores the time in seconds of now
ts = time.time()

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

### clear all data in redis first
r.flushall()
## header
headers = {
    'Content-type' :'application/json'
    }
### sent ping request test the connection
for hostname in SERVER_POOL:
    try:
        ## sent get request to app server
        response_from_app = requests.get(
            url = "http://"+ hostname+ "/pingtest", 
            headers= headers,
            timeout=5
            )

        if response_from_app.status_code == 200:
            ### app server addrress + port
            r.hset("vmserv_free", hostname, 1)
            ### last connection time
            r.hset("vmserv_lastconn", hostname, time.time())
            r.hset("vmserv_taskid", hostname, '-1') 
            r.hset("vmserv_jobid", hostname, '-1') 
            
        else:
            ### app server addrress + port
            r.hset("vmserv_free", hostname, 0)
    except:
        ### app server addrress + port
        r.hset("vmserv_free", hostname, 0)


# ### hashmap name
# vmserv_free
# vmserv_lastconn
# vmserv_taskid
# vmserv_jobid
# vmserv_jobcount

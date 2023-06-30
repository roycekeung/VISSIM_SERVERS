#################################################################################
#
#   Description : - loadbalancer
#                   
#
#################################################################################

import random
# from itertools import cycle
import itertools 
import enum
import time
from datetime import datetime
import logging

# from threading import Thread, Lock
# mutex = Lock()
# ### mutex lock 
# mutex.acquire()
# ### then change shared global val
# ### mutex release 
# mutex.release()


__all__ = [ 'LoadbalancerAlgo', 'LoadBalancer', 'random', 'itertools', 'enum', 'time', 'logging']  

from app import r
# import redis
# POOL = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
# r = redis.Redis(connection_pool=POOL)

def round_robin(iter):
    # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
    return next(iter)

class LoadbalancerAlgo(enum.IntEnum):
    random = 0
    roundrobin = 1


class LoadBalancer():

    __tolerance_losttime = 60*60     ## 1 hours
    __waittime = 2*60    ## 2 min
    
    ### Singleton
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(LoadBalancer, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def __init__(self, tolerance_losttime=3600 , *args, **kwargs ):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        self.__tolerance_losttime = tolerance_losttime
        self.logger = logging.getLogger('/LoadBalancer')
        self.logger.info("a LoadBalancer class object is created with id address %s"% id(self))
        print("a LoadBalancer class object is created with id address ", id(self))

    ### --- --- --- --- --- --- create --- --- --- --- --- ---
    
    def select_server( self, taskid, jobid, algorithm, max_pool=4):
        # __tolerance_losttime = 60*60   ## 1 hours
        # waittime = 2*60   ## 2 min
        starttime = time.time()
        
        
        ## get app server keys
        app_server_pool = r.hkeys("vmserv_free")
        # print("app_server_pool: " , app_server_pool, "at ", datetime.now())     ### debugtest
        # print("app_server_pool_status: " , r.hvals("vmserv_free"), "at ", datetime.now())     ### debugtest

        ### check if available for this task to use app server
        count = r.hvals('vmserv_taskid').count(str(taskid))
        if count>=max_pool or all(isfree == str(0) for isfree in r.hvals('vmserv_free')) :
            # print("count: " , count, "r.hvals('vmserv_free'): ", r.hvals('vmserv_free'))     ### debugtest
            return None
            
        selected_server = None
        if algorithm == LoadbalancerAlgo.random:
            while True:
                selected_server = random.choice(app_server_pool)
                if r.hget('vmserv_free', selected_server)==str(1) and \
                    time.time()-float(r.hget('vmserv_lastconn', selected_server))<self.__tolerance_losttime:
                    LoadBalancer.set_free_by_host(selected_server, 0)
                    r.hset('vmserv_taskid', selected_server, taskid)
                    r.hset('vmserv_jobid', selected_server, jobid)
                    # print("selected_server: " , selected_server, "taskid: ", taskid, "jobid: ",jobid)     ### debugtest
                    return selected_server
                elif time.time() - starttime >self.__waittime:
                    return None
            
        elif algorithm == LoadbalancerAlgo.roundrobin:
            while True:
                selected_server = round_robin(itertools.cycle(app_server_pool))
                if r.hget('vmserv_free', selected_server)==str(1) and\
                    time.time()-float(r.hget('vmserv_lastconn', selected_server))<self.__tolerance_losttime:
                    LoadBalancer.set_free_by_host(selected_server, 0)
                    r.hset('vmserv_taskid', selected_server, taskid)
                    r.hset('vmserv_jobid', selected_server, jobid)
                    # print("selected_server: " , selected_server, "taskid: ", taskid, "jobid: ",jobid)     ### debugtest
                    return selected_server
                elif time.time() - starttime >self.__waittime:
                    return None

        else:
            return Exception('unknown algorithm: %s' % algorithm)


    ### --- --- --- --- --- --- set/ update --- --- --- --- --- ---
    def set_free_by_jobid( self, jobid, free):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                r.hset('vmserv_free', hostname, free)
                if (int(free) >=1):
                    self.jobcount_incr(taskid= int(r.hget('vmserv_taskid', hostname)))
                    # print("vmserv_jobcount: " , r.hget('vmserv_jobcount', str(jobid)))     ### debugtest
                    r.hset('vmserv_taskid', hostname, '-1')
                    r.hset('vmserv_jobid', hostname, '-1')
                    print("vmserv_free: " , hostname, r.hget('vmserv_free', hostname), "is set to be free")     ### debugtest
                return {hostname:free}
        return None

    @staticmethod
    def set_free_by_host( hostname, free):
        if (r.hexists("vmserv_free", hostname)):
            r.hset("vmserv_free", hostname, free)
            if (int(free) >=1):
                r.hset('vmserv_taskid', hostname, '-1')
                r.hset('vmserv_jobid', hostname, '-1')
            return {hostname:free}
        else:
            None
            
    @staticmethod
    def update_lastconn_by_jobid( jobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                r.hset("vmserv_lastconn", hostname, time.time())
                return {hostname:r.hget("vmserv_lastconn", hostname)}
        return None
    
    @staticmethod
    def update_lastconn_by_host( hostname):
        if (r.hexists("vmserv_lastconn", hostname)):
            r.hset("vmserv_lastconn", hostname, time.time())
            return {hostname:r.hget("vmserv_lastconn", hostname)}
        else:
            None

    def change_taskid(self, taskid, newtaskid):
        for hostname, val in r.hgetall('vmserv_taskid').items():
            if int(val) == taskid:
                r.hset("vmserv_taskid", hostname, newtaskid)
                
    def change_jobid(self, jobid, newjobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                r.hset("vmserv_jobid", hostname, newjobid)

    def set_tolerance_losttime(self, timestamp):
        if (isinstance(timestamp, int)):
            self.__tolerance_losttime = timestamp
            return True
        else:
            return False

    ### --- --- --- --- --- --- getter --- --- --- --- --- ---    
    def get_taskids_inuse(self):
        return r.hgetall("vmserv_taskid")

    def get_jobids_inuse(self):
        return r.hgetall("vmserv_taskid")
    
    def get_hostnames_by_taskid(self, taskid):
        hostname_ls = []
        for hostname, val in r.hgetall('vmserv_taskid').items():
            if int(val) == taskid:
                hostname_ls.append(hostname) 
        return hostname_ls
    
    def get_hostname_by_jobid(self, jobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                return hostname
            
    def isfree_by_jobid(self, jobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                return r.hget("vmserv_free", hostname)
        return None
    
    @staticmethod
    def isfree_by_host( hostname):
        if (r.hexists("vmserv_lastconn", hostname)):
            return r.hget("vmserv_free", hostname)
        else:
            None        
            
    def get_lastconn_by_jobid(self, jobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                return {hostname:r.hget("vmserv_lastconn", hostname)}
        return None
    
    def get_lastconn_by_host(self, hostname):
        if (r.hexists("vmserv_lastconn", hostname)):
            return {hostname:r.hget("vmserv_lastconn", hostname)}
        else:
            None
    
    @staticmethod
    def get_jobcount_by_taskid( taskid):
        return int(r.hget('vmserv_jobcount', str(taskid)))
    
    def get_tolerance_losttime(self):
        return self.__tolerance_losttime 
    
    def get_server_numcount(self):
        return r.hlen('vmserv_free')
    
    def get_servers_ls(self):
        return r.hkeys('vmserv_free')
    
    ### --- --- --- --- --- --- incr --- --- --- --- --- ---
    def jobcount_incr(self, taskid):
        if (r.hexists("vmserv_jobcount", str(taskid))):
            r.hincrby("vmserv_jobcount", str(taskid), amount=1)
        else:
            r.hset('vmserv_jobcount', str(taskid), 1)

        return int(r.hget('vmserv_jobcount', str(taskid)))


    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    def delete_jobcount_by_taskid(self, taskid):
        r.hdel("vmserv_jobcount", str(taskid))

    def delete_server_by_host(self, hostname):
        r.hdel("vmserv_free", hostname)
        r.hdel("vmserv_lastconn", hostname)
        r.hdel("vmserv_taskid", hostname)
        r.hdel("vmserv_jobid", hostname)
        
    @staticmethod
    def cancel_task_by_taskid( taskid):
        for hostname, val in r.hgetall('vmserv_taskid').items():
            if int(val) == taskid:
                r.hset("vmserv_taskid", hostname, '-1')
                r.hset("vmserv_jobid", hostname, '-1')
          
    @staticmethod  
    def cancel_job_by_jobid( jobid):
        for hostname, val in r.hgetall('vmserv_jobid').items():
            if int(val) == jobid:
                r.hset("vmserv_taskid", hostname, '-1')
                r.hset("vmserv_jobid", hostname, '-1')  


# LoadBalancer.select_server(1, 1, LoadbalancerAlgo.roundrobin, 3)
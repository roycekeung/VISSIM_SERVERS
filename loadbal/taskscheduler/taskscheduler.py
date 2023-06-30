
from app.models import * 
from app import r
from app.config import STORAGE_SERVER, QUE_SERVER, LOADBAL_SERVER

import time
from datetime import datetime
import requests
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=2))


def scheduledPingTask():
    app_server_totalnum = r.hlen('vmserv_free')
    app_servers_ls = r.hkeys('vmserv_free')
    for serv_id in range(app_server_totalnum):
        hostname = app_servers_ls[serv_id]
        try:
            response = s.get( url = "http://%s/pingtest" %hostname, \
                headers={'Connection':'close'}, \
                timeout=5)
            if response.status_code == 200:
                r.hset("vmserv_lastconn", hostname, time.time())
                print(f'serv_id{serv_id} hostname {hostname} connection success at {datetime.now()}')
                r.hset("vmserv_free", hostname, 1 if response.json().get("isrunning")==False else 0)

            else:
                print(f'serv_id{serv_id} hostname {hostname} connection failed at {datetime.now()}')
                r.hset("vmserv_free", hostname, 0)
        except HTTPError or Exception as err:
            print(f'serv_id{serv_id} hostname {hostname}; error occurred: {err} at {datetime.now()}') 
            r.hset("vmserv_free", hostname, 0)
            



def scheduledUnfinishedJobCheck():
    print(f'*** *** *** scheduled Unfinished Job Check start at {datetime.now()}*** *** ***')   ### debug test
    __failed_time = 15*60   ## 15min
    __tolerance_losttime = 5*60   ## 5min
    
    storage_server = STORAGE_SERVER[0]
    
    app_server_totalnum = r.hlen('vmserv_free')
    running_taskids_ls = r.hkeys('vmserv_jobcount')
    for n in range(len(running_taskids_ls)):
        taskid = int(running_taskids_ls[n])
        
        try:
            response = requests.get( url = "http://%s/failedjoblist?taskid=%d&failedtime=%d" %(storage_server, taskid, __failed_time), \
                headers={'Content-type': 'application/json', 'Connection':'close'}
                )
            if response.status_code == 200:
                if response.json().get("joblen")==0 :
                    pass
                else:
                    
                    for jobid in response.json().get("jobidls"):
                        ## resend sim
                        taskid = response.json().get("taskid")
                        jobname = response.json().get("jobname")
                        maxpool = app_server_totalnum
                        print(f'[-] taskid {taskid} jobid {jobid} need to resend sim again at {datetime.now()}')
                        
                        resendSim(taskid , jobid, jobname, maxpool, __tolerance_losttime)

            else:
                print(f'jobid{jobid} storage_server {storage_server} connection failed at {datetime.now()}')
        except HTTPError or Exception as err:
            print(f'jobid{jobid} storage_server {storage_server}; error occurred: {err} at {datetime.now()}') 
            
    print(f'*** *** *** scheduled Unfinished Job Check end at {datetime.now()}*** *** ***')   ### debug test
            
            

# JobRootfile
def resendSim(taskid, jobid, jobname,maxpool, tolerance_losttime = 5*60):
    starttime = time.time()
    sleeptime = 3
    Lb_hostname = LOADBAL_SERVER[0]
    storage_server = STORAGE_SERVER[0]
    ServSelectAlgo = 0  ## random
    ## header
    binheaders = {'Content-type': 'application/octet-stream', 'Connection':'close'}
    jsheaders = {'Content-type': 'application/json', 'Connection':'close'}
    
    selected_server =None
    sim_sent_Flag = False
    while sim_sent_Flag is False and (time.time() - starttime )< tolerance_losttime:
        ### --- --- --- --- --- --- --- --- loadbalancer --- --- --- --- --- --- --- --- 
        try:
            ### --- --- --- --- ask loadbalancer server for free app server --- --- --- --- 
            response = requests.post(
                url = "http://"+ Lb_hostname+ "/selectserver?taskid=%d&jobid=%d&algo=%d&maxpool=%d"\
                    %(taskid, jobid, ServSelectAlgo, maxpool), 
                    headers = jsheaders)

            if response.status_code == 200:
                selected_server = response.json().get("hostname")
            
        except Exception or HTTPError as err:
            # # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
            # print ('   - taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
            pass

        ### no free server selected so ignore the sim post request
        if (selected_server is None):
            # wait
            time.sleep(sleeptime)
            continue
        
        
        ### --- --- --- --- --- --- --- --- sim --- --- --- --- --- --- --- --- 
        bindata = None
        try:
            ### --- --- --- --- ask storage server to take out jobrootfile --- --- --- --- 
            response = requests.get(
                url = "http://"+ storage_server+ "/jobrootfile?jobid=%d"\
                    %(jobid), 
                    headers = jsheaders)
            if response.status_code == 200:
                bindata = response.content
                # # logger.info('taskid %d - jobid %d - %s : jobrootfile get Successfully! '%(taskid, jobid, datetime.now()))
                print('   - taskid %d - jobid %d - %s : jobrootfile get Successfully!'%(taskid, jobid, datetime.now()))

        except Exception or HTTPError as err:
            # # logger.warning('taskid %d - job - %s : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
            print ('   - taskid %d - job %d - %s : when upload to apps, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
            pass

        
        try:
            ### --- --- --- --- post task rootfile to apps server --- --- --- --- 
            response = requests.post(
                url = "http://"+ selected_server+ "/runsim?jobid=%d&jobname=%s"\
                    %(jobid, jobname), 
                    data= bindata,
                    headers = binheaders)

            if response.status_code == 200:
                # jobid = response.json().get("jobid")
                # # logger.info('taskid %d - jobid %d - %s : job rootfile Sent out Successfully! '%(taskid, jobid, datetime.now()))
                print('   - taskid %d - jobid %d - %s : rootfile Sent out Successfully!'%(taskid, jobid, datetime.now()))
                sim_sent_Flag= True
            
        except Exception or HTTPError as err:
            # # logger.warning('taskid %d - job - %s : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
            print ('   - taskid %d - job %d - %s : when upload to apps, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
            pass

        ### sim post request is failed to send out
        if (sim_sent_Flag == False):
            ### --- --- --- --- --- --- --- --- loadbalancer --- --- --- --- --- --- --- --- 
            try:
                ### need to tell back to the loadbalancer that server is failed of connection
                response = requests.post(
                    url = "http://"+ Lb_hostname+ "/freejobserver?&jobid=%d&isfree=%d"\
                        %( jobid, 1), 
                        headers = jsheaders)

            except Exception or HTTPError as err:
                # # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                # print ('   - taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
                pass
        
        # wait
        time.sleep(sleeptime)

# force to taskkill no respond vissim obj by brute force
def scheduledTaskkill(failed_time):
    print(f'*** *** *** scheduled taskkill no respond vissim obj start at {datetime.now()}*** *** ***')   ### debug test

    lastconn_dt = r.hgetall('vmserv_lastconn')
    server_address_hist = []
    
    for key, val in lastconn_dt.items():
        server_address , port = key.split(":")
        
        
        if(server_address not in server_address_hist):
            try:
                response = requests.post( url = "http://%s/taskkillcheck" %(key), \
                    headers={'Content-type': 'application/json', 'Connection':'close'}
                    )
                if response.status_code == 200:
                    NumNotRespond = response.json().get("NumNotRespond")
                    NumTaskkill = response.json().get("NumTaskkill")
                    print(f' * Num of app NotRespond {NumNotRespond} is found at {datetime.now()} in app hostname {key}')
                    print(f' * Num of app NotRespond {NumTaskkill} is taskkilled at {datetime.now()} in app hostname {key}')   

                else:
                    print(f' * app_server {key} connection failed at {datetime.now()}')
            except HTTPError or Exception as err:
                print(f' * app_server {key} ; error occurred: {err} at {datetime.now()}') 
            
            
            server_address_hist.append(server_address)
        
        
        
        

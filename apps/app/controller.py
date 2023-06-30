import string
from flask import jsonify, make_response
from sqlalchemy.sql.sqltypes import Boolean
from flask_restful import Resource, reqparse
from flask_restful.inputs import boolean
from flask import request

import time

from app import compute, app

import psutil   ###  process and system utilities
import os


### for test checking whether server exist
class PingTest(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        
    def get(self):
        self.logger.info("server had been ping; computer running is %b"%compute.isrunning())
        return make_response(jsonify({
            "status_code" : "200",
            "message" : "Pong",
            "isrunning" : compute.isrunning()
            }), 200)


### slot for receiving computation simulation request
class RunSim(Resource):
    timeout = 10   ### in sec default time out for asking the availability of computation

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('jobname', type = str, default='New folder', location = 'args', required=False, help="jobname should be in str") \
            .parse_args()

        if reqparse.request.headers['Content-Type'] == 'application/octet-stream': 
            jobid = args['jobid']
            jobname = args['jobname']
            
            
            succeed_flag = False
            timeout_start = time.time()
            while (time.time() < timeout_start + self.timeout):
                if (not compute.isrunning() and len(compute.getinputio())==0):
                    content = request.get_data()     ### request.files['file'].read()
                    compute.init(jobid = jobid, input = content, jobname= jobname)
                    succeed_flag = True
    
                    break
                else:
                    time.sleep(2)

    
            self.logger.info("RunSim request Successful! added job into application server" if (succeed_flag) else "Request Timeout")
            return make_response(jsonify({
                "status_code" : "200" if (succeed_flag) else "408",
                "jobid" : jobid, 
                "message": "Success! added job into application server" if (succeed_flag) else "Request Timeout" 
                }), 200 if (succeed_flag) else 408 )
                    
        else:
            self.logger.error("Unsupported Media Type")
            return make_response(jsonify(status_code=415, message= " Unsupported Media Type"))


class RunStat(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        ### status on this applicatiion server end
        jobid = compute.getjobid()
        eval = compute.geteval()
        
        runtime = compute.getruntime_informat()
        isrunning = compute.isrunning()
        sleeptime = compute.getsleeptime()
        
        curresultsnum = compute.getcurresultsnames()
        
        self.logger.info("RunStat request; jobid={jobid} eval={eval} runtime={runtime} isrunning={isrunning} sleeptime={sleeptime} curresultsnum={curresultsnum} isserverfound={isserverfound}".format(\
            jobid, eval, runtime, sleeptime, curresultsnum, True))
        return make_response(jsonify({
            "jobid": jobid,
            "eval" : eval,
            "runtime": runtime,
            "isrunning": isrunning,
            "sleeptime": sleeptime, 
            "curresultsnum": curresultsnum,
            "isserverfound": True,
            }), 200)


class RunLog(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        ### status on this applicatiion server end
        jobid = compute.getjobid()
        log = compute.getcurlog()

        self.logger.info("RunLog request; jobid={jobid} log={log}".format(\
            jobid, log))
        return make_response(jsonify({
            "status_code" : "200",
            "jobid" : jobid,
            "log" : log
            }), 200)

class TaskkillCheck(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
            
    def post(self):
        NumTaskkill = 0
        
        respond = os.popen(f'tasklist /v /fi "STATUS eq Not Responding" /fi "memusage gt 100000"').read().strip().split('\n')
        
        vissim_inf_container = []
        
        for i in range(len(respond)):
            # skip first 2 lines (cols and lines)
            if (i >= 2):
                elm = respond[i].split()

                ## no matter what ver some r eg. VISSIM100.exe
                imgName = "VISSIM" 
                if imgName in respond[i]:
                    vissim_inf_container.append(respond[i])     
                    pid = int(elm[1])
                    try:
                        p = psutil.Process(pid) 
                        p.terminate()
                        NumTaskkill+=1
                        
                    except:
                        pass
        self.logger.info("RunLog request; NumNotRespond={NumNotRespond} NumTaskkill={NumTaskkill}".format(\
            len(vissim_inf_container), NumTaskkill))
        return make_response(jsonify({
            "status_code" : "200",
            "NumNotRespond": len(vissim_inf_container),
            "NumTaskkill": NumTaskkill,
            }), 200)


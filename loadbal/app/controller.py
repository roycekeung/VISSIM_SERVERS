from flask import jsonify, make_response
from sqlalchemy.sql.sqltypes import Binary, Boolean
from flask_restful import Resource, reqparse
from flask_restful.inputs import boolean

from requests.exceptions import HTTPError

from app.config import Config
from app.models import LoadBalancer, LoadbalancerAlgo
from app import Lb

from datetime import datetime

class SelectServer(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('algo', type = int, default=0, location = 'args', required=False, help="algo should be in int") \
            .add_argument('maxpool', type = int, default=1, location = 'args', required=False, help="maxpool should be in int") \
            .parse_args()


        taskid = args['taskid']
        jobid = args['jobid']
        algo = args['algo']
        maxpool = args['maxpool']
        # print("from SelectServer post ", "taskid: " , taskid, "jobid: ", jobid, "maxpool: ", maxpool, f"at {datetime.now()}")     ### debugtest

        if (algo==0):
            selected_server = Lb.select_server(taskid, jobid, algorithm= LoadbalancerAlgo.random, max_pool=maxpool)
        elif (algo==1):
            selected_server = Lb.select_server(taskid, jobid, algorithm= LoadbalancerAlgo.roundrobin, max_pool=maxpool)
        else:
            self.logger.error("SelectServer request; taskid={taskid} jobid={jobid} algo={algo} maxpool={maxpool} message={message}".format(\
                taskid, jobid, algo, maxpool, "have no such algo"))
            return make_response(jsonify({
            "status_code" : "400",
            "taskid": taskid,
            "jobid": jobid,
            "algo" : algo,
            "maxpool" :maxpool,
            "message": "have no such algo"
            }), 400)

        if (selected_server):
            self.logger.info("SelectServer request; taskid={taskid} jobid={jobid} algo={algo} maxpool={maxpool} hostname={selected_server} message={message}".format(\
                taskid, jobid, algo, maxpool, selected_server, "server is selected from the pool"))
            print("from SelectServer post ", "taskid: " , taskid, "jobid: ", jobid, "selected_server", selected_server)     ### debugtest
            return make_response(jsonify({
            "status_code" : "200",
            "taskid": taskid,
            "jobid": jobid,
            "algo" : algo,
            "maxpool" :maxpool,
            "hostname" : selected_server,
            "message": "server is selected from the pool"
            }), 200)
        else:
            self.logger.warning("SelectServer request; taskid={taskid} jobid={jobid} algo={algo} maxpool={maxpool} hostname={selected_server} message={message}".format(\
                taskid, jobid, algo, maxpool, None, "server pool doesnt contain free server/ task have used servers which is limited by maxpool amount"))
            print("from SelectServer post ", "taskid: " , taskid, "jobid: ", jobid, "selected_server", selected_server)     ### debugtest
            return make_response(jsonify({
            "status_code" : "500",
            "taskid": taskid,
            "jobid": jobid,
            "algo" : algo,
            "maxpool" :maxpool,
            "hostname" : None,
            "message": "server pool doesnt contain free server/ task have used servers which is limited by maxpool amount"
            }), 500)
            
class FreeJobServer(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
         
    ### reset server free, bool when failed to send request to app server for computing
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('isfree', type = int, default=0, location = 'args', required=False, help="isfree should be in int either 0 or 1") \
            .parse_args()

        jobid = args['jobid']
        isfree = args['isfree']
        print("from FreeJobServer post: " , "jobid: ", jobid, "isfree: ", isfree, f"at {datetime.now()}")     ### debugtest
        response = Lb.set_free_by_jobid(jobid, isfree)
        
        if (response):
            self.logger.info("FreeJobServer request; jobid={jobid} hostname={selected_server} server_status={server_status} message={message}".format(\
                jobid, list(response.keys())[0], list(response.values())[0], "server status is reset"))
            return make_response(jsonify({
            "status_code" : "200",
            "jobid": jobid,
            "hostname" : list(response.keys())[0],
            "server_status" : list(response.values())[0],
            "message": "server status is reset"
            }), 200)
        else:
            self.logger.warning("FreeJobServer request; jobid={jobid} hostname={selected_server} message={message}".format(\
                jobid, None, "server status is failed on reset, related jobid might not exist"))
            return make_response(jsonify({
            "status_code" : "500",
            "jobid": jobid,
            "hostname" : None,
            "message": "server status is failed on reset, related jobid might not exist"
            }), 500)
            
    ### update server free, bool when finish computing received results from app server/ send request to app server successfully
    def put(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('isfree', type = int, default=0, location = 'args', required=False, help="isfree should be in int either 0 or 1") \
            .parse_args()

        jobid = args['jobid']
        isfree = args['isfree']
        print("from FreeJobServer post: " , "jobid: ", jobid, "isfree: ", isfree, f"at {datetime.now()}")     ### debugtest
        response = Lb.set_free_by_jobid(jobid, isfree)
        Lb.update_lastconn_by_host(list(response.keys())[0])
        
        if (response):
            self.logger.info("FreeJobServer request; jobid={jobid} hostname={selected_server} server_status={server_status} message={message}".format(\
                jobid, list(response.keys())[0], list(response.values())[0], "server status is updated"))
            return make_response(jsonify({
            "status_code" : "200",
            "jobid": jobid,
            "hostname" : list(response.keys())[0],
            "server_status" : list(response.values())[0],
            "message": "server status is updated"
            }), 200)
        else:
            self.logger.warning("FreeJobServer request; jobid={jobid} hostname={selected_server} message={message}".format(\
                jobid, None, "server status is failed on update, related jobid might not exist"))
            return make_response(jsonify({
            "status_code" : "500",
            "jobid": jobid,
            "hostname" : None,
            "message": "server status is failed on update, related jobid might not exist"
            }), 500)

class FreeServer(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 
        
    ### reset server free, bool when failed to send request to app server for computing
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('hostname', type = str, default=None, location = 'args', required=False, help="hostname should be in string") \
            .add_argument('isfree', type = int, default=0, location = 'args', required=False, help="isfree should be in int either 0 or 1") \
            .parse_args()

        hostname = args['hostname']
        isfree = args['isfree']

        response = Lb.set_free_by_host(hostname, isfree)
        
        if (response):
            self.logger.info("FreeServer request; hostname={selected_server} server_status={server_status} message={message}".format(\
                list(response.keys())[0], response.values[0], "server status is reset"))
            return make_response(jsonify({
            "status_code" : "200",
            "hostname" : hostname,
            "server_status" : response.values[0],
            "message": "server status is reset"
            }), 200)
        else:
            self.logger.warning("FreeServer request; hostname={selected_server} message={message}".format(\
                hostname, "server status is failed on request or maybe server doesnt exist"))
            return make_response(jsonify({
            "status_code" : "500",
            "hostname" : hostname,
            "message": "server status is failed on request or maybe server doesnt exist"
            }), 500)

    ### get server free, hostname
    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('hostname', type = str, default=None, location = 'args', required=False, help="hostname should be in string") \
            .parse_args()

        hostname = args['hostname']

        bool = Lb.isfree_by_host(hostname)
        
        if (bool== True or bool==False):
            self.logger.info("FreeServer request; hostname={selected_server} server_status={server_status} message={message}".format(\
                hostname, bool, "server status is obtained"))
            return make_response(jsonify({
            "status_code" : "200",
            "hostname" : hostname,
            "server_status" : bool,
            "message": "server status is obtained"
            }), 200)
        elif (bool==None):
            self.logger.warning("FreeServer request; hostname={selected_server} server_status={server_status} message={message}".format(\
                hostname, None, "server status is failed on request or maybe server doesnt exist"))
            return make_response(jsonify({
            "status_code" : "500",
            "hostname" : hostname,
            "server_status" : None,
            "message": "server status is failed on request or maybe server doesnt exist"
            }), 500)


class JobCount(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 
        
    ### get server free, hostname
    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

        taskid = args['taskid']

        count = Lb.get_jobcount_by_taskid(taskid)
        
        self.logger.info("JobCount request; taskid={taskid} jobcount={count} message={message}".format(\
            taskid, count, "server status is obtained"))
        return make_response(jsonify({
        "status_code" : "200",
        "taskid" : taskid,
        "jobcount" : count,
        "message": "jobcount is accumulation of the finished jobs"
        }), 200)


class CancelTask(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 
        
    ### get server free, hostname
    def delete(self):
        args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

        taskid = args['taskid']

        Lb.cancel_task_by_taskid(taskid)
        
        self.logger.info("CancelTask request; taskid={taskid} message={message}".format(\
            taskid, "task is canceled"))
        return make_response(jsonify({
        "status_code" : "200",
        "taskid" : taskid,
        "message": "task is canceled"
        }), 200)

class CancelJob(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 
        
    ### get server free, hostname
    def delete(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()

        jobid = args['jobid']

        Lb.cancel_job_by_jobid(jobid)
        
        self.logger.info("CancelJob request; jobid={jobid} message={message}".format(\
            jobid, "jobid is canceled"))
        return make_response(jsonify({
        "status_code" : "200",
        "jobid" : jobid,
        "message": "job is canceled"
        }), 200)

class EndTaskRunning(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger') 
        
    ### end the taskid counting in redis
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

        taskid = args['taskid']

        Lb.delete_jobcount_by_taskid(taskid)
        
        self.logger.info("EndTaskRunning request; taskid={taskid} message={message}".format(\
            taskid, "jobcount is deleted"))
        return make_response(jsonify({
        "status_code" : "200",
        "taskid" : taskid,
        "message": "jobcount is deleted"
        }), 200)

from flask import jsonify, make_response, send_file
from sqlalchemy.sql.sqltypes import Boolean
from flask_restful import Resource, reqparse
from flask_restful.inputs import boolean
from flask import request

from app.models import LocationEnum, TypeEnum, Task, Job

from app.config import *

import uuid
import os

import json

import requests
from requests.exceptions import HTTPError

from io import BytesIO
import shutil
import re

### set up zipmode ; By default the ZIP module only store data, to compress it you can do this
import zipfile
from zipfile import error
try:
    import zlib
    zipmode= zipfile.ZIP_DEFLATED
except:
    zipmode= zipfile.ZIP_STORED
   
# ### --- --- --- for html web visual --- --- --- 
# from flask import render_template
# from app import app
# @app.route('/ping', methods=['GET'])
# def home():
#     return render_template("index.html")

   
### for test checking whether server exist
class PingTest(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        
    def get(self):
        self.logger.info("server had been ping")
        return make_response(jsonify({
            "status_code" : "200",
            "message" : "Pong"
            }), 200)
        
class TaskRootfile(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')


    def post(self):
        if reqparse.request.headers['Content-Type'] == 'application/octet-stream':
            args = reqparse.RequestParser() \
                .add_argument('name', type = str, default=None, location = 'args', required=False, help="name should be in string") \
                .add_argument('locationid', type = int, default=0, location = 'args', required=False, help="locationid should be in int enum") \
                .add_argument('typeid', type = int, default=1, location = 'args', required=False, help="typeid should be in int enum") \
                .parse_args()

            name = args['name']
            locationid = args['locationid']
            typeid = args['typeid']
            
            taskobj = Task(name=name, location= locationid, type= typeid, isfinished=None, isrunning=True)
            LocationEnum.add_task_by_locid(locationid, taskobj)
            TypeEnum.add_task_by_typeid(typeid, taskobj)
            
            typeid = taskobj.get_locid_by_name(name)
            locationid = taskobj.get_typeid_by_name(name)
            taskid = taskobj.get_taskid_by_name(name)
            taskid = taskobj.get_taskid
            if taskid is None :
                return make_response(jsonify(status_code=404, message= " task is failed on initialization"))
            
            bin_data= request.get_data()     
            folderPath = os.path.join(os.getcwd(), 'storage')
            folderPath = os.path.join(folderPath, 'rootfile')
            folderPath = os.path.join(folderPath, str(taskid))

            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
            uuidname = str(uuid.uuid1())
            tmpfilename = '%s.zip'%uuidname
            binary_file_path = os.path.join(folderPath, tmpfilename) 
            with open(binary_file_path, 'wb') as f:
                f.write(bin_data)
                
            taskobj.set_rootfile_by_taskid(taskid, os.path.join(folderPath, tmpfilename))

              
            print("Task with taskid %d is successfully created and backup in %s"%(taskid, folderPath))
            self.logger.info("TaskRootfile request; name={name} taskid={taskid} locationid={locationid} typeid={typeid} message={message}".format(\
                name, taskid, locationid, typeid, "Task Backup succeeded"))
            return make_response(jsonify({
                "status_code" : "200",
                "name": name,
                "taskid": taskid,
                "locationid": locationid, 
                "typeid": typeid, 
                "message": "Task Backup succeeded"
                }), 200)
        else:
            return make_response(jsonify(status_code=415, message= " Unsupported Media Type"))

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

        taskid = args['taskid']
        try:
            if (Task.is_task_exist(taskid) ):
                bdata_address = Task.get_rootfile_by_taskid(taskid)
                if (bdata_address is not None):
                    memory_file = open(bdata_address, 'rb')
                    binary_file = memory_file.read()
                    response = make_response(binary_file)
                    response.headers.set('Content-Type', 'application/octet-stream')
                    self.logger.info("TaskRootfile request; taskid={taskid} message={message}".format(\
                        taskid, "Task get succeeded"))
                    return response
                else:
                    self.logger.error("TaskRootfile request; taskid={taskid} message={message}".format(\
                        taskid, "Task is not yet uploaded"))
                    return make_response(jsonify({
                        "taskid": taskid,
                        "message": 'Task is not yet uploaded',
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.error("TaskRootfile request; taskid={taskid} message={message}".format(\
                    taskid, "task Not Found"))

                return make_response(jsonify({
                    "taskid": taskid,
                    "message": 'task Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))

class JobRootfile(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()

        jobid = args['jobid']
        try:
            if (Job.is_job_exist_by_jobid(jobid) ):
                
                taskid = Job.get_taskid_by_jobid(jobid)
                taskroot_address = Task.get_rootfile_by_taskid(taskid)
                taskname = Task.get_name_by_taskid(taskid)
                sig_address = Job.get_sig_by_jobid(jobid)
                folderPath = os.path.join(os.getcwd(), 'tmp')
                rootfilefolderpath = os.path.join(folderPath, taskname)
                
                if (taskroot_address != None and sig_address != None):
                    memory_file = open(taskroot_address, 'rb')
                    binary_file = memory_file.read()
                    
                    ### --- --- take out taskrootfile --- ---
                    with zipfile.ZipFile(file = taskroot_address, mode = 'r') as taskrootzip:
                        ## unzip taskrootfile
                        taskrootzip.extractall(folderPath)
                        sig_FileDirname= 'sig'
                        # Wlaking top-down from the root
                        for root, dirnames, files in os.walk(rootfilefolderpath):
                            AllFileDirNames = dirnames
                            break
                        for FileDirNames in AllFileDirNames:
                            if re.findall(r"($sig$)", FileDirNames):
                                sig_FileDirname = FileDirNames
                        ### del all sig from initial seed in taskrootfile
                        shutil.rmtree(os.path.join(rootfilefolderpath,sig_FileDirname))
                    
                        
                    ### --- --- replace sig --- ---
                    with zipfile.ZipFile(file = sig_address, mode = 'r') as sigzip:
                        ## unzip sigfile
                        sigzip.extractall(folderPath)
                        
                    # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                    jobrootfileinmem = BytesIO()
                    with zipfile.ZipFile(mode='w', file=jobrootfileinmem, compression = zipfile.ZIP_DEFLATED) as myzip:
                        for root, dirs, files in os.walk(rootfilefolderpath):
                            for file in files:
                                myzip.write(os.path.join(root, file), 
                                            os.path.relpath(os.path.join(root, file), 
                                                            os.path.join(rootfilefolderpath, '..')))

                    response = make_response(jobrootfileinmem.getvalue())
                    response.headers.set('Content-Type', 'application/octet-stream')
                        
                    ### del all jobrootfile in tmp
                    shutil.rmtree(rootfilefolderpath)
                    
                    self.logger.info("JobRootfile request; name={taskname} jobid={jobid} message={message}".format(\
                        taskname, jobid, "JobRootfile get succeeded"))
                    return response
                else:
                    self.logger.warning("TaskRootfile request; jobid={jobid} message={message}".format(\
                        jobid, "Taskrootfile or sig is not yet uploaded"))
                    return make_response(jsonify({
                        "jobid": jobid,
                        "message": 'Taskrootfile or sig is not yet uploaded',
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.warning("TaskRootfile request; jobid={jobid} message={message}".format(\
                    jobid, "job Not Found"))
                return make_response(jsonify({
                    "jobid": jobid,
                    "message": 'job Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))


class JobEval(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    # def post(self):
    #     args = reqparse.RequestParser() \
    #         .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
    #         .add_argument('eval', type = int, default=0, location = 'args', required=False, help="eval should be in int") \
    #         .parse_args()

    #     jobid = args['jobid']
    #     eval = args['eval']
    #     taskid = Job.get_taskid_by_jobid(jobid)

    #     Job.get_eval_by_jobid(jobid, eval)

    #     print("eval Backup succeeded for jobid %d"%jobid)
    #     return make_response(jsonify({
    #         "status_code" : "200",
    #         "taskid": taskid,
    #         "jobid": jobid, 
    #         "popid": Job.get_popid_by_jobid(jobid),
    #         "gen": Job.get_gen_by_jobid(jobid),
    #         "subgen": Job.get_subgen_by_jobid(jobid),
    #         "message": "Success! eval backup into storage"
    #         }), 200)

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()
        ### if gen, subgen r -1 means None, the algo type could be calibration

        jobid = args['jobid']
        taskid = Job.get_taskid_by_jobid(jobid)
        popid = Job.get_popid_by_jobid(jobid)
        gen = Job.get_gen_by_jobid(jobid)
        subgen = Job.get_subgen_by_jobid(jobid)
        eval = Job.get_eval_by_jobid(jobid)

        self.logger.info("JobEval request; taskid={taskid} eval={eval} message={message}".format(\
            taskid, eval, "JobEval get succeeded"))
        return make_response(jsonify({
            "status_code" : "200",
            "taskid": taskid,
            "jobid": jobid,
            "popid": popid,
            "gen": gen,
            "subgen": subgen,
            "eval" : eval
            }), 200)


class JobSigCreate(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        if reqparse.request.headers['Content-Type'] == 'application/octet-stream':
            args = reqparse.RequestParser() \
                .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
                .add_argument('popid', type = int, default=None, location = 'args', required=False, help="popid should be in int") \
                .add_argument('gen', type = int, default=1, location = 'args', required=False, help="gen should be in int or -1") \
                .add_argument('subgen', type = int, default=0, location = 'args', required=False, help="subgen should be in int or -1") \
                .parse_args()
            ### if gen, subgen r -1 means None, the algo type could be calibration

            taskid = args['taskid']
            popid = args['popid']
            gen = args['gen'] if args['gen'] != -1 else None
            subgen = args['subgen'] if args['subgen'] != -1 else None
            
            jobobj = Job(popid=popid, gen=gen, subgen=subgen, sig= None)
            Job.add_job_by_taskid(taskid, jobobj)
            jobid = jobobj.get_jobid

            
            bin_data= request.get_data()     
            folderPath = os.path.join(os.getcwd(), 'storage')
            folderPath = os.path.join(folderPath, 'input')
            folderPath = os.path.join(folderPath, 'sig')
            folderPath = os.path.join(folderPath, str(taskid))
            folderPath = os.path.join(folderPath, str(jobid))

            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

            binary_file_path = os.path.join(folderPath, '%s.zip'%uuid.uuid1()) 
            with open(binary_file_path, 'wb') as f:
                f.write(bin_data)

            Job.set_sig_by_jobid(jobid, binary_file_path)
            
            #Job.set_issucceed_by_taskid(jobid, issucceed)

            self.logger.info("JobSigCreate request; taskid={taskid} jobid={jobid} message={message}".format(\
                taskid, jobid, "Job is created and sig Backup succeeded"))
            print("Job with jobid %d is created and Sig is successfully backup in %s"%(jobid, folderPath))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "jobid": jobid, 
                "popid": popid,
                "gen": gen,
                "subgen": subgen,
                "message": "Job is created and sig Backup succeeded"
                }), 200)
        else:
            self.logger.error("Unsupported Media Type")
            return make_response(jsonify(status_code=415, message= " Unsupported Media Type"))

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()
        ### if gen, subgen r -1 means None, the algo type could be calibration

        jobid = args['jobid']
        taskid = Job.get_taskid_by_jobid(jobid)
        popid = Job.get_popid_by_jobid(jobid)
        gen = Job.get_gen_by_jobid(jobid)
        subgen = Job.get_subgen_by_jobid(jobid)
            
        try:
            if (Job.is_job_exist_by_taskid(taskid, popid, gen, subgen) ):
                bdata_address = Job.get_sig_by_taskid(taskid, popid, gen, subgen)
                if (bdata_address is not None):
                    memory_file = open(bdata_address, 'rb')
                    binary_file = memory_file.read()
                    response = make_response(binary_file)
                    response.headers.set('Content-Type', 'application/octet-stream')
                    self.logger.info("JobSigCreate request; taskid={taskid} jobid={jobid} message={message}".format(\
                        taskid, jobid, "sig files get succeeded"))
                    return response
                else:
                    self.logger.error("JobSigCreate request; taskid={taskid} jobid={jobid} message={message}".format(\
                        taskid, jobid, "sig files not yet uploaded"))
                    return make_response(jsonify({
                        "taskid": taskid,
                        "jobid": jobid,
                        "popid": popid,
                        "gen": gen,
                        "subgen": subgen,
                        "message": 'sig files not yet uploaded',
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.error("JobSigCreate request; taskid={taskid} jobid={jobid} message={message}".format(\
                    taskid, jobid, "job Not Found"))
                return make_response(jsonify({
                    "taskid": taskid,
                    "jobid": jobid,
                    "popid": popid,
                    "gen": gen,
                    "subgen": subgen,
                    "message": 'job Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))
        
### should have one JobResult request and JobResults multiple
### not yet done
class JobResult(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        if reqparse.request.headers['Content-Type'] == 'application/octet-stream':
            args = reqparse.RequestParser() \
                .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
                .add_argument('eval', type = float, default=1, location = 'args', required=False, help="eval should be in int") \
                .add_argument('issucceed', type = int, default=True, location = 'args', required=False, help="issucceed should be in bool") \
                .parse_args()

            jobid = args['jobid']
            eval = args['eval']
            issucceed = True if args['issucceed']>=1 else False
            taskid = Job.get_taskid_by_jobid(jobid)
            
            bin_data= request.get_data()     
            folderPath = os.path.join(os.getcwd(), 'storage')
            folderPath = os.path.join(folderPath, 'results')
            folderPath = os.path.join(folderPath, str(taskid))
            folderPath = os.path.join(folderPath, str(jobid))

            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

            binary_file_path = os.path.join(folderPath, 'eval=%f_%s.zip'%(eval,uuid.uuid1())) 
            with open(binary_file_path, 'wb') as f:
                f.write(bin_data)

            Job.set_eval_by_jobid(jobid, eval)
            Job.set_result_by_jobid(jobid, binary_file_path)
            Job.set_issucceed_by_jobid(jobid, issucceed)
            
        
            print("Job results with jobid %d is successfully created and backup in %s"%(jobid, folderPath))
            self.logger.info("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                taskid, jobid, "Job resullts Backup succeeded"))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "jobid": jobid, 
                "popid": Job.get_popid_by_jobid(jobid),
                "gen": Job.get_gen_by_jobid(jobid),
                "subgen": Job.get_subgen_by_jobid(jobid),
                "eval" : eval,
                "message": "Job resullts Backup succeeded"
                }), 200)
        else:
            self.logger.error("Unsupported Media Type")
            return make_response(jsonify(status_code=415, message= " Unsupported Media Type"))

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()
        ### if gen, subgen r -1 means None, the algo type could be calibration

        jobid = args['jobid']
        taskid = Job.get_taskid_by_jobid(jobid)
        popid = Job.get_popid_by_jobid(jobid)
        gen = Job.get_gen_by_jobid(jobid)
        subgen = Job.get_subgen_by_jobid(jobid)
        eval = Job.get_eval_by_jobid(jobid)
            
        try:
            if (Job.is_job_exist_by_taskid(taskid, popid, gen, subgen) ):
                bdata_address = Job.get_result_by_taskid(taskid, popid, gen, subgen)
                if (bdata_address is not None):
                    memory_file = open(bdata_address, 'rb')
                    binary_file = memory_file.read()
                    response = make_response(binary_file)
                    response.headers.set('Content-Type', 'application/octet-stream')
                    self.logger.info("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                       taskid, jobid, "Job resullts get succeeded"))
                    return response
                else:
                    self.logger.error("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                        taskid, jobid, "Results files not yet uploaded"))
                    return make_response(jsonify({
                        "taskid": taskid,
                        "jobid": jobid,
                        "popid": popid,
                        "gen": gen,
                        "subgen": subgen,
                        "eval" : eval,
                        "message": 'Results files not yet uploaded',
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.error("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                    taskid, jobid, "job Not Found"))
                return make_response(jsonify({
                    "taskid": taskid,
                    "jobid": jobid,
                    "popid": popid,
                    "gen": gen,
                    "subgen": subgen,
                    "eval" : eval,
                    "message": 'job Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))
        

class JobSigResult(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('withroot', type = int, default=0, location = 'args', required=False, help="withtaskroot should be in bool") \
            .parse_args()

        jobid = args['jobid']
        withroot = True if args['withroot']>=1 else False
        try:
            if (Job.is_job_exist_by_jobid(jobid) ):
                
                taskid = Job.get_taskid_by_jobid(jobid)
                bdata_address = Job.get_result_by_jobid(jobid)
                taskname = Task.get_name_by_taskid(taskid)
                sig_address = Job.get_sig_by_jobid(jobid)
                folderPath = os.path.join(os.getcwd(), 'tmp')
                rootfilefolderpath = os.path.join(folderPath, taskname)
                
                taskroot_address = Task.get_rootfile_by_taskid(taskid)
                
                if (taskroot_address != None and sig_address != None and bdata_address != None):
                    if (withroot):
                        memory_file = open(taskroot_address, 'rb')
                        binary_file = memory_file.read()
                        
                        ### --- --- take out taskrootfile --- ---
                        with zipfile.ZipFile(file = taskroot_address, mode = 'r') as taskrootzip:
                            ## unzip taskrootfile
                            taskrootzip.extractall(folderPath)
                            sig_FileDirname= 'sig'
                            # Wlaking top-down from the root
                            for root, dirnames, files in os.walk(rootfilefolderpath):
                                AllFileDirNames = dirnames
                                break
                            for FileDirNames in AllFileDirNames:
                                if re.findall(r"($sig$)", FileDirNames):
                                    sig_FileDirname = FileDirNames
                            ### del all sig from initial seed in taskrootfile
                            shutil.rmtree(os.path.join(rootfilefolderpath,sig_FileDirname))
                        
                    ### --- --- replace or addin sig files --- ---
                    with zipfile.ZipFile(file = sig_address, mode = 'r') as sigzip:
                        ## unzip sigfile
                        sigzip.extractall(folderPath)
                        
                    ### --- --- addin result db files --- ---  
                    with zipfile.ZipFile(file = bdata_address, mode = 'r') as dbzip:
                        ## unzip sigfile
                        dbzip.extractall(rootfilefolderpath)
                        
                    # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                    jobSigResultfileinmem = BytesIO()
                    with zipfile.ZipFile(mode='w', file=jobSigResultfileinmem, compression = zipfile.ZIP_DEFLATED) as myzip:
                        for root, dirs, files in os.walk(rootfilefolderpath):
                            for file in files:
                                myzip.write(os.path.join(root, file), 
                                            os.path.relpath(os.path.join(root, file), 
                                                            os.path.join(rootfilefolderpath, '..')))

                    response = make_response(jobSigResultfileinmem.getvalue())
                    response.headers.set('Content-Type', 'application/octet-stream')
                        
                    ### del all jobrootfile in tmp
                    shutil.rmtree(rootfilefolderpath)
                    self.logger.info("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                       taskid, jobid, "Job signal and resullts get succeeded"))
                    return response
                else:
                    message = 'Taskrootfile is {Taskrootfile} or sig {sig} or result is {result}'.format(
                            Taskrootfile = "not None" if taskroot_address else None, sig = "not None" if sig_address else None , result= "not None" if bdata_address else None)
                    self.logger.error("JobResult request; taskid={taskid} jobid={jobid} message={message}".format(\
                       taskid, jobid, message))
                    return make_response(jsonify({
                        "jobid": jobid,
                        "message": message,
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.error("JobResult request; jobid={jobid} message={message}".format(\
                    jobid, "job Not Found"))    
                return make_response(jsonify({
                    "jobid": jobid,
                    "message": 'job Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))

        

class JobLog(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .add_argument('issucceed', type = int, default=0, location = 'args', required=False, help="issucceed should be in bool") \
            .parse_args()

        jobid = args['jobid']
        issucceed = True if args['issucceed']>=1 else False
        taskid = Job.get_taskid_by_jobid(jobid)

        log_message= str(request.get_json()['log']).strip().replace("\n", "")
        Job.set_log_by_jobid(jobid, log_message)
        Job.set_issucceed_by_jobid(jobid, issucceed)
            

        print("log Backup succeeded for jobid %d"%jobid)
        self.logger.info("JobLog request; taskid={taskid} jobid={jobid} message={message}".format(\
            taskid, jobid, "Success! log backup into storage"))
        return make_response(jsonify({
            "status_code" : "200",
            "taskid": taskid,
            "jobid": jobid, 
            "popid": Job.get_popid_by_jobid(jobid),
            "gen": Job.get_gen_by_jobid(jobid),
            "subgen": Job.get_subgen_by_jobid(jobid),
            "eval" : Job.get_eval_by_jobid(jobid),
            "message": "Success! log backup into storage"
            }), 200)

    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()
        ### if gen, subgen r -1 means None, the algo type could be calibration

        jobid = args['jobid']
        taskid = Job.get_taskid_by_jobid(jobid)
        popid = Job.get_popid_by_jobid(jobid)
        gen = Job.get_gen_by_jobid(jobid)
        subgen = Job.get_subgen_by_jobid(jobid)
        eval = Job.get_eval_by_jobid(jobid)

        try:
            if (Job.get_log_by_jobid(taskid, popid, gen, subgen) ):
                log_data = Job.get_result_by_taskid(taskid, popid, gen, subgen)
                if (log_data is not None):
                    self.logger.info("JobLog request; taskid={taskid} jobid={jobid} message={message}".format(\
                        taskid, jobid, "see logs arg"))
                    return make_response(jsonify({
                        "status_code" : "200",
                        "taskid": taskid,
                        "jobid": jobid,
                        "popid": popid,
                        "gen": gen,
                        "subgen": subgen,
                        "eval" : eval,
                        "log_data": log_data, 
                        "message": "see logs arg"
                        }), 200)
                            
                else:
                    self.logger.warning("JobLog request; taskid={taskid} jobid={jobid} message={message}".format(\
                        taskid, jobid, "no Log"))
                    return make_response(jsonify({
                        "taskid": taskid,
                        "jobid": jobid,
                        "popid": popid,
                        "gen": gen,
                        "subgen": subgen,
                        "eval" : eval,
                        "log_data": None, 
                        "message": 'no Log',
                        "status_code" : "404"
                        }), 404)
            else:
                self.logger.error("JobLog request; taskid={taskid} jobid={jobid} message={message}".format(\
                    taskid, jobid, "job Not Found"))
                return make_response(jsonify({
                    "taskid": taskid,
                    "jobid": jobid,
                    "popid": popid,
                    "gen": gen,
                    "subgen": subgen,
                    "eval" : eval,
                    "log_data": None,
                    "message": 'job Not Found',
                    "status_code" : "404"
                    }), 404)

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}') 
            return make_response(jsonify({"message": f'HTTP error occurred: {http_err}'}))
        except Exception as err:
            print(f'Other error occurred: {err}') 
            return make_response(jsonify({"message": f'Other error occurred: {err}'}))


class TaskStatus(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

    def get(self):
        taskid = self.args['taskid']

        if (Task.is_task_exist(taskid)):
            taskname = Task.get_name_by_taskid(taskid)
            locationname = LocationEnum.get_locname_by_locid(Task.get_locid_by_taskid(taskid))
            typename = TypeEnum.get_typename_by_typeid(Task.get_typeid_by_taskid(taskid))
            isfinished = Task.is_finished_by_taskid(taskid)
            isrunning = Task.is_running_by_taskid(taskid)
            runtime = Task.get_runtime_by_taskid(taskid)
            strruntime = str(runtime)
            self.logger.info("TaskStatus request; taskid={taskid} taskname={taskname} locationname={locationname} typename={typename} isfinished={isfinished} isrunning={isrunning} strruntime={strruntime} message={message}".format(\
                taskid, taskname, locationname, typename, isfinished, isrunning, strruntime, "task Not Found"))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "taskname": taskname,
                "locationname" : locationname,
                "typename": typename,
                "isfinished": isfinished,
                "isrunning" : isrunning,
                "runtime" :strruntime
                }), 200)
        else:
            self.logger.error("TaskStatus request; taskid={taskid} message={message}".format(\
                taskid, "task Not Found"))
            return make_response(jsonify({
                "taskid": taskid,
                "message": 'task Not Found',
                "status_code" : "404"
                }), 404)


class JobStatus(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()

    def get(self):
        jobid = self.args['jobid']

        if (Job.is_job_exist_by_jobid(jobid)):
            taskid = Job.get_taskid_by_jobid(jobid)
            jobname = Task.get_name_by_taskid(taskid)
            popid = Job.get_popid_by_jobid(jobid)
            eval = Job.get_eval_by_jobid(jobid)
            gen = Job.get_gen_by_jobid(jobid)
            subgen = Job.get_subgen_by_jobid(jobid)
            log = Job.get_log_by_jobid(jobid)
            issucceed = Job.is_succeed_by_jobid(jobid)
            runtime = Job.get_runtime_by_jobid(jobid)
            self.logger.info("JobStatus request; jobid={jobid} taskid={taskid} jobname={jobname} popid={popid} eval={eval} gen={gen} subgen={subgen} log={log} issucceed={issucceed} runtime={runtime}".format(\
                jobid, taskid, jobname, popid, eval, gen, subgen, log, issucceed, runtime))
            return make_response(jsonify({
                "status_code" : "200",
                "jobid" : jobid, 
                "taskid": taskid,
                "jobname": jobname,
                "popid": popid,
                "eval" : eval,
                "gen": gen,
                "subgen": subgen,
                "log" : log,
                "issucceed" :issucceed,
                "runtime": runtime
                }), 200)
        else:
            self.logger.error("JobStatus request; jobid={jobid} message={message}".format(\
                jobid, "job Not Found"))
            return make_response(jsonify({
                "jobid": jobid,
                "message": 'job Not Found',
                "status_code" : "404"
                }), 404)


### not yet done
### input: measurements naming Excel : delay Measurements, Veh Travel Time Measurements, data collection Measurements, que measurements
### return: Result Summary Excel : Ave_queue, Max_queue, delay Measurement, Travel Time, Vehicle Throughout, Duration of Congestion, \
### Waiting time - Stop Delay, std of Avg Queue in 300sec 12 intervals
class ResultSum(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()

    def get(self):
        jobid = self.args['jobid']

        if (Job.is_job_exist_by_jobid(jobid)):
            taskid = Job.get_taskid_by_jobid(jobid)
            popid = Job.get_popid_by_jobid(jobid)
            eval = Job.get_eval_by_jobid(jobid)
            
            issucceed = Job.is_succeed_by_jobid(jobid)
            runtime = Job.get_runtime_by_jobid(jobid)
            
            self.logger.info("ResultSum request; jobid={jobid} taskid={taskid} popid={popid} eval={eval} issucceed={issucceed} runtime={runtime}".format(\
                jobid, taskid, popid, eval, issucceed, runtime))
            return make_response(jsonify({
                "status_code" : "200",
                "jobid" : jobid, 
                "taskid": taskid,
                "popid": popid,
                "eval" : eval,
                "issucceed" :issucceed,
                "runtime": runtime
                }), 200)
        else:
            self.logger.error("ResultSum request; jobid={jobid} message={message}".format(\
                jobid, "job Not Found"))
            return make_response(jsonify({
                "jobid": jobid,
                "message": 'job Not Found',
                "status_code" : "404"
                }), 404)

### not yet done
class ResultsSum(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('jobid', type = int, default=1, location = 'args', required=False, help="jobid should be in int") \
            .parse_args()

    def get(self):
        jobid = self.args['jobid']

        if (Job.is_job_exist_by_jobid(jobid)):
            taskid = Job.get_taskid_by_jobid(jobid)
            popid = Job.get_popid_by_jobid(jobid)
            eval = Job.get_eval_by_jobid(jobid)
            
            issucceed = Job.is_succeed_by_jobid(jobid)
            runtime = Job.get_runtime_by_jobid(jobid)
            self.logger.info("ResultSum request; jobid={jobid} taskid={taskid} popid={popid} eval={eval} issucceed={issucceed} runtime={runtime}".format(\
                jobid, taskid, popid, eval, issucceed, runtime))
            return make_response(jsonify({
                "status_code" : "200",
                "jobid" : jobid, 
                "taskid": taskid,
                "popid": popid,
                "eval" : eval,
                "issucceed" :issucceed,
                "runtime": runtime
                }), 200)
        else:
            self.logger.error("ResultsSum request; jobid={jobid} message={message}".format(\
                jobid, "job Not Found"))
            return make_response(jsonify({
                "jobid": jobid,
                "message": 'job Not Found',
                "status_code" : "404"
                }), 404)



## all jobids related to taskid
class TaskJobList(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .parse_args()

    def get(self):
        taskid = self.args['taskid']

        if (Task.is_task_exist(taskid)):
            isfinished= Task.is_finished_by_taskid(taskid)
            isrunning= Task.is_running_by_taskid(taskid)
            jobid_ls = Job.get_jobids_by_taskid(taskid)
            joblen = len(jobid_ls) if jobid_ls!=None else 0
            joblsissucceed = Job.is_succeed_jobls_by_taskid(taskid)
            self.logger.info("TaskJobList request; taskid={taskid} jobid_ls={jobid_ls} joblen={joblen} isfinished={isfinished} isrunning={isrunning} joblsissucceed={joblsissucceed}".format(\
                taskid, jobid_ls, joblen, isfinished, isrunning, joblsissucceed))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "jobidls" : jobid_ls, 
                "joblen" : joblen,
                "taskisfinished": isfinished,
                "taskisrunning": isrunning,
                "joblsissucceed" :joblsissucceed
                }), 200)
        else:
            self.logger.error("TaskJobList request; taskid={taskid} message={message}".format(\
                taskid, 'task Not Found'))
            return make_response(jsonify({
                "taskid": taskid,
                "message": 'task Not Found',
                "status_code" : "404"
                }), 404)


class FailedJobList(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .add_argument('failedtime', type = int, default=1, location = 'args', required=False, help="failedtime should be in int sec") \
            .parse_args()

    def get(self):
        taskid = self.args['taskid']
        failedtime= self.args['failedtime']

        if (Task.is_task_exist(taskid)):
            jobname = Task.get_name_by_taskid(taskid)
            jobid_ls = Job.get_failed_jobids_by_taskid(taskid, failedtime)
            joblen = len(jobid_ls) if jobid_ls!=None else 0

            self.logger.info("FailedJobList request; taskid={taskid} jobname={jobname} jobid_ls={jobid_ls} joblen={joblen}".format(\
                taskid, jobname, jobid_ls, joblen))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "jobname": jobname,
                "jobidls" : jobid_ls, 
                "joblen" : joblen
                }), 200)
        else:
            self.logger.error("FailedJobList request; taskid={taskid} message={message}".format(\
                taskid, 'task Not Found'))
            return make_response(jsonify({
                "taskid": taskid,
                "message": 'task Not Found',
                "status_code" : "404"
                }), 404)


class EndTask(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.args = reqparse.RequestParser() \
            .add_argument('taskid', type = int, default=1, location = 'args', required=False, help="taskid should be in int") \
            .add_argument('isfinished', type = int, default=1, location = 'args', required=False, help="isfinished should be in int") \
            .add_argument('isrunning', type = int, default=1, location = 'args', required=False, help="isrunning should be in int") \
            .parse_args()

    def post(self):
        taskid = self.args['taskid']
        isfinished= True if self.args['isfinished'] >0 else False
        isrunning= True if self.args['isrunning']  >0 else False

        if (Task.is_task_exist(taskid)):
            jobname = Task.get_name_by_taskid(taskid)

            Task.set_finish_by_taskid(taskid, bool=isfinished)
            Task.set_running_by_taskid(taskid, bool=isrunning)
            
            lb_server = LOADBAL_SERVER[0]
            ## header
            jsheaders = {'Content-type': 'application/json', 'Connection':'close'}
            try:
                response = requests.get( url = "http://%s/endtaskrunning?taskid=%d" %(lb_server, taskid), \
                    headers=jsheaders
                    )
            except HTTPError or Exception as err:
                print(f'taskid{taskid} LOADBAL_SERVER {lb_server}; error occurred: {err}') 
                
            print(f'taskid {taskid} ;isfinished {isfinished}; isrunning {isrunning}') 
            self.logger.info("EndTask request; taskid={taskid} isfinished={isfinished} isrunning={isrunning}".format(\
                taskid, isfinished, isrunning))
            return make_response(jsonify({
                "status_code" : "200",
                "taskid": taskid,
                "isfinished": isfinished,
                "isrunning" : isrunning
                }), 200)

        else:
            self.logger.error("EndTask request; taskid={taskid} message={message}".format(\
                taskid, 'task Not Found'))
            return make_response(jsonify({
                "taskid": taskid,
                "message": 'task Not Found',
                "status_code" : "404"
                }), 404)



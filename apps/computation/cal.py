#################################################################################
#
#   Description : first in first out ques for (simulation, optimization run) and 
#               (the jobs done sending back to clients)
#               keep running in infinity in a sub thread beside the main thread 
#               whereas backend server running on
#
##################################################################################


from asyncio.windows_events import NULL
import threading 
import requests
from requests.exceptions import HTTPError
import time

import json
from io import BytesIO
import base64

import os
import glob
import re
import shutil

from datetime import datetime

import logging

import socket
This_hostname = socket.gethostbyname(socket.gethostname())

import zlib
import asyncio

import win32com.client as com



from app.config import *

# from que.pikaconnect import channel, connection, properties, mandatory
import pika

### set up zipmode ; By default the ZIP module only store data, to compress it you can do this
import zipfile
from zipfile import error
try:
    import zlib
    zipmode= zipfile.ZIP_DEFLATED
except:
    zipmode= zipfile.ZIP_STORED


def find_AlldirInThisFile( search_path):

   # Wlaking top-down from the root
   for root, dirnames, files in os.walk(search_path):
      result = dirnames
      break

   return result


# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT)
# logger = logging.getLogger(__name__)


class RunCal():
    ### data
    __inputio = BytesIO()
    __resultoutputio = BytesIO()
    __sig = None
    __curlog = ''
    __jobname = ''
    __clear_targets=set()   ### address of residual target
    
    ### result
    __eval = None
    
    ### id and category
    __jobid = None

    ### compute inf
    __SimResNum = 10
    __starttime = None
    __isrunnging= False
    __issucceed = None
    
    ### port num, no need if seperate server files
    ## int(app.config['SERVER_NAME'].split(':')[1]
    __port_num = 0

    ### log  
    logger = None
    
    ### tmp computation target  
    folderPath = None

    sleeptime = 3

    def __init__(self, sec = 3, *args, **kwargs):
        self.logger = logging.getLogger(__name__)

        self.sleeptime = sec

        print("a Calbase is created with id address ", id(self.__class__))
        
        ### get current file directory path
        self.folderPath = os.path.join(os.getcwd(), 'tmp')
        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)
            
        
        ### pika connect to messageque properties
        self.credentials = pika.PlainCredentials(username='vissim_outputque', password='123456')

        self.properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,  
        )
        self.mandatory=False



    # Destructor
    def __del__(self):
        # ### break connection to messagemq in order to flush
        # connection.close()
        # print(" [x] output que connection close")
        print(" [x] cal object deleted")
        
    ### --- --- --- --- --- --- getter --- --- --- --- --- --- 
    @staticmethod
    def getinputio():
        return RunCal.__inputio.getvalue()
    
    @staticmethod
    def getinputioobj():
        return RunCal.__inputio
    
    @staticmethod
    def getresultoutputio():
        return RunCal.__resultoutputio.getvalue()
    
    @staticmethod
    def getresultoutputioobj():
        return RunCal.__resultoutputio

    @staticmethod
    def getsig():
        return RunCal.__sig

    @staticmethod
    def getcurlog():
        return RunCal.__curlog
    
    @staticmethod
    def getjobname():
        return RunCal.__jobname
    
    @staticmethod
    def geteval():
        return RunCal.__eval

    @classmethod
    def getjobid(cls):
        return RunCal.__jobid

    def getruntime_insec(self):
        if (self.isrunning()):
            return time.time()- self.__starttime
        else:
            return None

    def getruntime_informat(self):
        if (self.isrunning()):
            return time.strftime('%H:%M:%S', time.gmtime(time.time()- self.__starttime))
        else:
            return None

    @classmethod
    def getsleeptime(cls):
        return RunCal.sleeptime

    @classmethod
    def getsimresnum(cls):
        return RunCal.__SimResNum

    @classmethod
    def getissucceed(cls):
        return RunCal.__issucceed
    
    def getcurresultsnames(self):
        AllFileDirNames = find_AlldirInThisFile(os.path.join(self.folderPath, RunCal.__jobname))
        results_FileDirname= None
        for FileDirNames in AllFileDirNames:
            if re.findall(r"(results$)", FileDirNames):
                results_FileDirname = FileDirNames
                
        if (results_FileDirname is None or len(AllFileDirNames)==0):
            return None
        
        resultfolderPath = os.path.join(os.path.join(self.folderPath, RunCal.__jobname), results_FileDirname)
        if os.path.exists(resultfolderPath):
            return os.listdir(resultfolderPath)
        else:
            return None

                

    ### --- --- --- --- --- --- set --- --- --- --- --- --- 
    @classmethod
    def setlogger(cls, **kwargs):
        RunCal.logger = kwargs.get('logger')

    @classmethod
    def init(cls, jobid, input, jobname):
        ### sim basic param setting
        RunCal.setjobid(jobid)
        RunCal.setinputio(input)
        RunCal.setjobname(jobname)
        
    @classmethod
    def setinputio(cls, input):
        RunCal.__inputio.write(input)
        
    @classmethod
    def setresultoutputio(cls, output):
        RunCal.__resultoutputio.write(output)
        
    @staticmethod
    def setsig(sig):
        RunCal.__sig  = sig

    @staticmethod
    def addcurlog(log):
        try:
            RunCal.__curlog += log
        except:
            RunCal.__curlog += ""
            
    @classmethod
    def setjobname(cls, jobname):
        RunCal.__jobname = jobname

    @staticmethod
    def seteval(eval):
        RunCal.__eval = eval

    @classmethod
    def setjobid(cls, id):
        RunCal.__jobid = id

    @staticmethod
    def setstartnow():
        RunCal.__starttime = time.time()

    @classmethod
    def setrunning(cls, bool):
        RunCal.__isrunnging = bool

    @classmethod
    def setsleeptime(cls, sec):
        RunCal.sleeptime = sec

    @classmethod
    def setsimresnum(cls, simnum):
        RunCal.__SimResNum = simnum

    @classmethod
    def setissucceed(cls, bool):
        RunCal.__issucceed = bool


    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    @classmethod
    async def clear(cls, jobfolderPath):
        ### data
        RunCal.__inputio = BytesIO()
        RunCal.__resultoutputio = BytesIO()
        RunCal. __sig = None
        RunCal.__curlog = ''
        RunCal.__jobname = ''
        RunCal.__eval = None

        RunCal.__jobid = None
        RunCal.__starttime = None
        RunCal.__isrunnging= False
        RunCal.__issucceed= None
        RunCal.__SimResNum = 10
        
        RunCal.__clear_targets.add(jobfolderPath)
    
        ####    comment for tmp trial  
        ### delete all used files
        try:
            await asyncio.sleep(2)
            for targetfolderPath in RunCal.__clear_targets:
                # if (len(os.listdir(targetfolderPath)) != 0):
                #     for root, dirs, files in os.walk(jobfolderPath):
                #         for file in files:
                #             # await os.remove(os.path.join(root, file))
                #             os.remove(os.path.join(root, file))
                # else:
                #     os.rmdir(targetfolderPath)  ## rm empty folder
                #     RunCal.__clear_targets.remove(targetfolderPath)
                
                shutil.rmtree(targetfolderPath)
                RunCal.__clear_targets.remove(targetfolderPath)
        except:
            ## del next time
            return
                
            


    ### --- --- --- --- --- --- check --- --- --- --- --- --- 
    @classmethod
    def isrunning(cls):
        return RunCal.__isrunnging

    ### --- --- --- --- --- --- runninf computation --- --- --- --- --- --- 
    async def start(self):

        # inifinitive function running main thread
        while True:
            
            if (RunCal.isrunning() ==  False and RunCal.getinputio()):

                RunCal.setstartnow()
                RunCal.setrunning(True)
                print( f'running jobid{RunCal.getjobid()} {RunCal.getjobname()} at {datetime.now()}')   #### debugtest
                        
                ###  1 unzip zipall rootfile from memory bytes to local hard disc  
                RunCal.getinputioobj().seek(0)
                with zipfile.ZipFile(file=RunCal.getinputioobj(), mode='r') as inputzipbin:
                    inputzipbin.extractall(self.folderPath)
                
                
                # ### 2 unzip rootfile to tmp dirfile 
                # with open(os.path.join(self.folderPath , "jobid%s.zip"%self.__jobid), 'wb') as inputrootbin:
                #     inputrootbin.write(RunCal.getinput())
                # with zipfile.ZipFile(os.path.join(self.folderPath , "jobid%s.zip"%self.__jobid), 'r') as inputrootzip:
                #     inputrootzip.extractall(self.folderPath)
                
                jobfolderPath = os.path.join(self.folderPath, RunCal.__jobname)
                AllFileDirNames = find_AlldirInThisFile(jobfolderPath)

                ## initiate
                Vissim = None
                ## crash Flag check
                iscrashedonvm = False
                ### set up vissim and start running
                try:
                    ### target computation rootfile folder is empty
                    if ( len(os.listdir(jobfolderPath)) != 0 ):
                        # --- --- --- --- --- open Vissim --- --- --- --- ---
                        Vissim = com.DispatchEx("Vissim.Vissim-64.10") ### original
                        # Vissim = com.dynamic.Dispatch("Vissim.Vissim-64.10")
                        
                        inpx_Filename = glob.glob(os.path.join(jobfolderPath,'*.inpx'))[0]
                        layx_Filename = glob.glob(os.path.join(jobfolderPath,'*.layx'))[0]
                        flag_read_additionally  = False
                        
                        # --- --- --- --- --- Setup Vissim --- --- --- --- ---
                        ## Load a network:
                        Vissim.LoadNet(os.path.join(jobfolderPath, inpx_Filename) , flag_read_additionally)
                        ## Load a Layout:
                        Vissim.LoadLayout(os.path.join(jobfolderPath, layx_Filename))

                        # # --- --- --- --- --- Simulation Time --- --- --- --- --- 
                        # # simDuration does not include simWarmUpTime
                        # simWarmUpTime = 300   
                        # simDuration = 3600
                        # simInterval = 900

                        # Vissim.Simulation.SetAttValue('SimPeriod', simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("AreaMeasResFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("AreaMeasResToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("AreaMeasResInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("DataCollFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("DataCollToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("DataCollInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("DelaysFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("DelaysToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("DelaysInterval", simInterval)
                        # Vissim.Evaluation.SetAttValue("LinkResFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("LinkResToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("LinkResInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("NodeResFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("NodeResToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("NodeResInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("QueuesFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("QueuesToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("QueuesInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("VehNetPerfFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("VehNetPerfToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("VehNetPerfInterval", simDuration)
                        # Vissim.Evaluation.SetAttValue("VehTravTmsFromTime", simWarmUpTime)
                        # Vissim.Evaluation.SetAttValue("VehTravTmsToTime", simWarmUpTime+simDuration)
                        # Vissim.Evaluation.SetAttValue("VehTravTmsInterval", simDuration)

                        # # --- --- --- --- --- Simulation Setup --- --- --- --- --- 

                        # #setup multi run
                        # Vissim.Simulation.SetAttValue("NumRuns", 5)
                        # Vissim.Simulation.SetAttValue("RandSeedIncr", 2)
                        # Vissim.Simulation.SetAttValue("SimPeriod", simWarmUpTime+simDuration)
                        # Vissim.Simulation.SetAttValue("SimRes", 10)
                        # Vissim.Simulation.SetAttValue("UseAllCores", True)

                        # ### clean prev runs
                        for simRun in Vissim.Net.SimulationRuns:
                            Vissim.Net.SimulationRuns.RemoveSimulationRun(simRun) 
                        # ### do the run
                        # Vissim.Simulation.SetAttValue("SimBreakAt", simWarmUpTime+simDuration)
                        Vissim.Simulation.RunSingleStep()
                        Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1)
                        Vissim.Simulation.SetAttValue("UseMaxSimSpeed", True)
                        Vissim.Simulation.RunContinuous()
                        Vissim.Simulation.Stop()

                        # get avg delay
                        avgDelay = Vissim.Net.VehicleNetworkPerformanceMeasurement.AttValue('DelayAvg(Avg,Avg,All)')
                        print("net avg delay: ", avgDelay)
                        latentDemand = Vissim.Net.VehicleNetworkPerformanceMeasurement.AttValue('DemandLatent(Avg,Avg)')
                        print(" net latent demand: ", latentDemand)
                        self.seteval(avgDelay + latentDemand)
                        
                        ### force to close
                        Vissim.Exit()
                        Vissim = None
                    
                    if (len(self.getcurresultsnames()) == RunCal.getsimresnum()):
                        jobfolderPath = os.path.join(self.folderPath, RunCal.__jobname)
                        AllFileDirNames = find_AlldirInThisFile(jobfolderPath)
                        results_FileDirname= 'results'
                        for FileDirNames in AllFileDirNames:
                            if re.findall(r"(results$)", FileDirNames):
                                results_FileDirname = FileDirNames
                        resultfolderPath = os.path.join(jobfolderPath, results_FileDirname)
                        if not os.path.exists(resultfolderPath):
                            os.makedirs(resultfolderPath)
                            
                        # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                        RunCal.getresultoutputioobj().seek(0)
                        with zipfile.ZipFile(mode='w', file=RunCal.getresultoutputioobj(), compression = zipfile.ZIP_DEFLATED) as myzip:
                            for root, dirs, files in os.walk(resultfolderPath):
                                for file in files:
                                    myzip.write(os.path.join(root, file), 
                                                os.path.relpath(os.path.join(root, file), 
                                                                os.path.join(resultfolderPath, '..')))
                                    # print("filename: ", os.path.join(root, file))
                        RunCal.setissucceed(True)
                    else:
                        RunCal.addcurlog('sim is failed while running either vissim no respond or server internal errors') 
                        RunCal.setissucceed(False)
 
 
                    #     # 2 write to zip file in local hard disc and zip all files and sub folder in a folder dir     
                    #     # with zipfile.ZipFile('results.zip', 'w', compression = zipmode) as myzip:
                    #     #     for resultfilename in os.listdir(resultfolderPath):
                    #     #         resultfilePath = os.path.join(self.folderPath, resultfilename)
                    #     #         myzip.write(resultfilePath, os.path.basename(resultfilePath))
                            
                    #     # with open('results.zip', 'rb') as resultszip:
                    #     #     RunCal.setresultoutput(resultszip.read())
                    #     #     RunCal.setissucceed(True)

                        
                    # else:
                    #     ### it has the residual from previous run
                    #     pass
                    
                except Exception or zipfile.error as err:
                    ### if parse thru there means the computation failed
                    RunCal.setissucceed(False)
                    
                    ## crash Flag check
                    iscrashedonvm = True if RunCal.geteval() == None and Vissim != None else False
                        
                    ### force to close whether its opened or not
                    Vissim = None
                    
                    if (err is not None):
                        self.logger.warning('host %s - jobid %d - %r : when computing, error occurs %s '\
                            %(This_hostname, RunCal.getjobid(), datetime.now(), err))
                        RunCal.addcurlog('%s'% err) 
                        print('host %s - jobid %d - %r : when computing, error occurs %s '\
                            %(This_hostname, RunCal.getjobid(), datetime.now(), err)) 
                    else:
                        self.logger.warning('host %s - jobid %d - %r : when computing, Nonetype unknown error occurs'\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))
                        RunCal.addcurlog('%s'% err)
                        print('host %s - jobid %d - %r : when computing, Nonetype unknown error occurs'\
                            %(This_hostname,  RunCal.getjobid(), datetime.now())) 

                ### sent back inf to output que server
                try:
                    output = dict()
                    output['jobid'] = RunCal.getjobid()
                    output['issucceed'] = RunCal.getissucceed()
                    
                    if (RunCal.getresultoutputio() and RunCal.getissucceed()==True):
                        output['eval'] = RunCal.geteval()
                        output['content'] = base64.b64encode(RunCal.getresultoutputio()).decode('ascii')

                        results = json.dumps(output)
                        
                        ## default usually RabbitMQ will listen on port=5676 or port=5672
                        connection = pika.BlockingConnection(
                            pika.ConnectionParameters(
                                host=QUE_SERVER,
                                port=5672,
                                virtual_host='/',
                                credentials=self.credentials,
                                socket_timeout=30,
                                blocked_connection_timeout=30,
                                connection_attempts=5,
                                retry_delay=5.0))

                        channel = connection.channel()
                        print(" [x] output message que is connected")

                        channel.queue_declare(queue='results')

                        channel.basic_publish(exchange='', routing_key='results', body=results,properties=self.properties,mandatory=self.mandatory)
                        self.logger.info('host %s - jobid %d - %r : Sent results '\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))
                        print('host %s - jobid %d - %r : Sent results '\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))
                        
                        connection.close()
                        print(" [x] output message que connection is closed")

                    if (RunCal.getcurlog()):

                        output['content'] = RunCal.getcurlog()
                        output['iscrashedonvm'] = iscrashedonvm
                        logs = json.dumps(output)

                        ## default usually RabbitMQ will listen on port=5676 or port=5672
                        connection = pika.BlockingConnection(
                            pika.ConnectionParameters(
                                host=QUE_SERVER, 
                                port=5672,
                                virtual_host='/',
                                credentials=self.credentials,
                                socket_timeout=30,
                                blocked_connection_timeout=30,
                                connection_attempts=5,
                                retry_delay=5.0))

                        channel = connection.channel()
                        print(" [x] output message que is connected")

                        channel.queue_declare(queue='logs')

                        channel.basic_publish(exchange='', routing_key='logs', body=logs,properties=self.properties,mandatory=self.mandatory)
                        self.logger.info('host %s - jobid %d - %r : Sent logs '\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))
                        print('host %s - jobid %d - %r : Sent logs '\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))

                        connection.close()
                        print(" [x] output message que connection is closed")
                        
                except Exception or HTTPError or zipfile.error as err:
                    if (err is not None):
                        self.logger.warning('host %s - jobid %d - %r : when upload to output que, error occurs %s '\
                            %(This_hostname, RunCal.getjobid(), datetime.now(), err))
                        RunCal.addcurlog('%s'% err)
                        print('%s - host %s - %s: when upload to output que, error occurs %s '\
                            %(This_hostname, RunCal.getjobid(), datetime.now(), err)) 
                    else:
                        self.logger.warning('host %s - jobid %d - %r : when upload to output que, Nonetype unknown error occurs'\
                            %(This_hostname, RunCal.getjobid(), datetime.now()))
                        RunCal.addcurlog('%s'% err)
                        print('host %s - jobid %d - %r : when upload to output que, Nonetype unknown error occurs'\
                            %(This_hostname, RunCal.getjobid(), datetime.now())) 

                finally:

                    clearing = asyncio.create_task(RunCal.clear(jobfolderPath))
                    await clearing
                    # asyncio.run(RunCal.clear(jobname))

            else:
                pass

            # wait
            print(f'apps server sleep {self.sleeptime} sec at {datetime.now()}')    #### debugtest
            time.sleep(self.sleeptime)




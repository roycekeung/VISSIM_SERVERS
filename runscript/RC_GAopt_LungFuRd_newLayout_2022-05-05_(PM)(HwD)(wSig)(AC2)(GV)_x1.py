

from config import *
from variables import *
import VissimDemandRouting_LungFuRd


import sys
import os
import requests
from requests.exceptions import HTTPError
import json
import logging
from datetime import datetime
import time
import zipfile
import re
import random
import glob
from io import BytesIO
import pandas as pd
import sqlite3
import shutil

# logger = logging.getLogger(__name__)
# ### logging format setup for tracking run history
# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(
#     filename='runlog.log', 
#     level=logging.DEBUG, 
#     format=FORMAT,
#     datefmt='%m-%d %H:%M',
#     filemode='w')

    
### --- --- --- --- --- --- --- --- cutomized inputs --- --- --- --- --- --- --- --- 
casename = "LungFuRd_newLayout 2022-05-05 (PM)(HwD)(wSig)(AC2)(GV)_x1" #'{}'.format(random.randint(0,10000))  ### <--- change input here   ### eg. PokOiVissim 2021-05-05A (Scn 3a) (26AM) 7
locationid = LocationEnum.LungFungRd    ### <--- change input here
typeid = AlgoTypeEnum.NGA    ### <--- change input here

ServSelectAlgo = LoadbalancerAlgo.random    ### <--- change input here
Lbmaxpool = 8

rootfilefolderpath = r"D:\Royce\VISSIM_SERVERS\runscript\LungFuRd_newLayout 2022-05-05 (PM)(HwD)(wSig)(AC2)(GV)_x1"     ### <--- change input here
TdSigpath = r"D:\Royce\VISSIM_SERVERS\runscript\LungFuRd_newLayout 2022-05-05 (PM)(HwD)(wSig)(AC2)(GV)_x1\TDSigData_LungFuRd.xml"   ### <--- change input here
sigsBasenames = glob.glob( os.path.join( os.path.join(rootfilefolderpath, 'sig'),'*.sig') )    ### ls gen auto


numOfGen = 6   ### <--- change input here
numOfsubGen = 0   ### <--- change input here
popSize = 50   ### <--- change input here

cur_gen = 1
cur_subgen = 0

taskid = 1   ### <--- change automatically

Demandrate = 1  ### <--- change input here


### --- --- --- --- --- --- --- --- prepare global variables naming --- --- --- --- --- --- --- --- 
## host
Lb_hostname = LOADBAL_SERVER[0]
Storage_hostname = STORAGE_SERVER[0]
## header
binheaders = {'Content-type': 'application/octet-stream', 'Connection':'close'}
jsheaders = {'Content-type': 'application/json', 'Connection':'close'}

bestgenejobid = 0
besteval = 0

sleeptime = 3

### --- --- --- --- --- pre def of internal functions for excel--- --- --- --- ---  
def CreateDictOfNo2Name(df):
    No = df.loc[:,'No']
    features_x = df.loc[:,'Name']
                ## int, string
    return dict(zip(No, features_x))

def find_AlldirInThisFile( search_path):

    # Wlaking top-down from the root
    for root, dirnames, files in os.walk(search_path):
        result = dirnames
        break

    return result

# #### zip all files and sub folder in a folder dir
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

totalSimNo = 10          ### <--- change input here
### get current file directory path
currentPath = os.getcwd()


ReferenceExcel_path = os.path.join(currentPath , "Measurements Naming EL_LungFuRd.xlsx")      ### <--- change input here

## **** kindly remember if error raised of the xlrd dependent missing
##  to do this command line; pip install xlrd==1.2.0
## Since old version run with no error
Delay_df = pd.read_excel(ReferenceExcel_path, sheet_name="Delay Measurements") 
TravTm_df = pd.read_excel(ReferenceExcel_path, sheet_name="Vehicle Travel Time Measurement")
Queue_df = pd.read_excel(ReferenceExcel_path, sheet_name="Queue Counters")    
DataCollectVehCount_df = pd.read_excel(ReferenceExcel_path, sheet_name="Data Collection Measurements")  

AlldictsFromReferenceTable = list(map(CreateDictOfNo2Name , [Delay_df, TravTm_df, Queue_df, DataCollectVehCount_df]))




import DISCO2_PyModule_Vissim
# implement override class
class implVissimRunner(DISCO2_PyModule_Vissim.Runner_VissimAsync):

    popjobid_dict = dict()    ## key : tId(popid) ; value : jobid
    
    
    cur_gen = cur_gen
    cur_subgen = cur_subgen
    
    # called per (sub)generation, must complete all cases at method return
    def pyRunAll(self):
        global cur_gen, cur_subgen, taskid, bestgenejobid, besteval
        
        while True:
            # # returns the count of cases that have not had its eval value set
            # n = self.getRemainingRunCaseNum()
            # relies on TDSigConvertor Vissim sig file mappings, will always modify the same files
            tId = self.makeNextSigFiles()
            
            ### tId ==-1 means stop no more gene
            if (tId >= 0):   ### and n > 0
                
                ### --- --- --- --- --- --- --- --- sig --- --- --- --- --- --- --- --- 
                # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                sig_FileBasenames = glob.glob(os.path.join( os.path.join(rootfilefolderpath, 'sig'),'*.sig') )
                siginmem = BytesIO()
                with zipfile.ZipFile(mode='w', file=siginmem, compression = zipfile.ZIP_DEFLATED) as myzip:
                    for file in sig_FileBasenames:
                        myzip.write(os.path.join(rootfilefolderpath, file), 
                                    os.path.relpath(os.path.join(rootfilefolderpath, file), 
                                                    os.path.join(rootfilefolderpath, '..')))
                            # print("filename: ", os.path.join(root, file))
                            
                    
                # # 2 write to zip file in local hard disc and zip all files and sub folder in a folder dir 
                # AllFileDirNames = find_AlldirInThisFile(rootfilefolderpath)
                # sig_FileDirname = 'sigs'
                # for FileDirNames in AllFileDirNames:
                #     if re.findall(r"(sig)", FileDirNames):
                #         sig_FileDirname = FileDirNames
                #
                # sigfolderPath = os.path.join(rootfilefolderpath, sig_FileDirname)    
                # zippedsigfilename= f'{os.path.basename(rootfilefolderpath)}_sig.zip'
                # zipf = zipfile.ZipFile(zippedsigfilename, 'w', zipfile.ZIP_DEFLATED)
                # zipdir( sigfolderPath, zipf)
                # with open(zippedsigfilename, 'rb') as rootfilezip:
                #     binsigcontent = rootfilezip.read()
            
                try:
                    ### --- --- --- --- post job sig to storage server --- --- --- --- 
                    response = requests.post(
                        url = "http://"+ Storage_hostname+ "/jobsigcreate?taskid=%d&popid=%d&gen=%d&subgen=%d"\
                            %(taskid, tId, cur_gen, cur_subgen), 
                            headers = binheaders,
                            data= siginmem.getvalue()
                           )

                    if response.status_code == 200:
                        jobid = response.json().get("jobid")
                        # logger.info('taskid %d - jobid %d - %s : job sig Sent out Successfully! '%(taskid, jobid, datetime.now()))
                        print('taskid %d - jobid %d - %s : job sig Sent out Successfully!'%(taskid, jobid, datetime.now()))
                        self.popjobid_dict[tId] = jobid
                    elif response.status_code == 404:
                        # logger.warning('taskid %d - job - %s : when upload to storage, server not found '%( taskid, datetime.now()))
                        raise ('taskid %d - job - %s : data storage server Not Found.'%( taskid, datetime.now()))
                    elif response.status_code == 500:
                        # logger.warning('taskid %d - job - %s - : when upload to storage, error occurs Internal Server Error '%(taskid, datetime.now()))
                        raise ('taskid %d - job - %s : Internal Server Error'%(taskid, datetime.now()))
                    else :
                        # logger.warning('taskid %d - job - %s : when upload to storage, error occurs with status code %d '%( taskid, datetime.now(), response.status_code))
                        raise ('taskid %d - job - %s : error with status code %d'%(taskid, datetime.now(), response.status_code))

                except Exception or HTTPError as err:
                    # logger.warning('taskid %d - job - %s : when upload to storage, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
                    raise ('taskid %d - job - %s : when upload to storage, Nonetype unknown error occurs'%(taskid,  datetime.now()))


                
                selected_server =None
                sim_sent_Flag = False
                while sim_sent_Flag is False:
                    ### --- --- --- --- --- --- --- --- loadbalancer --- --- --- --- --- --- --- --- 
                    try:
                        ### --- --- --- --- ask loadbalancer server for free app server --- --- --- --- 
                        response = requests.post(
                            url = "http://"+ Lb_hostname+ "/selectserver?taskid=%d&jobid=%d&algo=%d&maxpool=%d"\
                                %(taskid, jobid, ServSelectAlgo, Lbmaxpool), 
                                headers = jsheaders)

                        if response.status_code == 200:
                            selected_server = response.json().get("hostname")
                            # logger.info('taskid %d - jobid %d - %s : %s server selected ! '%(taskid, jobid, datetime.now(), selected_server))
                            print('taskid %d - jobid %d - %s : %s server selected ! '%(taskid, jobid, datetime.now(), selected_server))
                        elif response.status_code == 404:
                            # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, server not found '%( taskid, jobid, datetime.now()))
                            print ('taskid %d - jobid %d - %s : loadbalancer server Not Found.'%( taskid, jobid, datetime.now()))
                        elif response.status_code == 500:
                            ### selected_server should be = None
                            selected_server = response.json().get("hostname")
                            # logger.warning('taskid %d - jobid %d - %s - : when connect to loadbalancer, error occurs Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                            print ('taskid %d - jobid %d - %s : Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                        else :
                            # logger.warning('taskid %d - jobid %d - %s : when upload to loadbalancer, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                            print ('taskid %d - jobid %d - %s : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))
                        
                        ### message from loadbalancer
                        # logger.info(response.json().get("message"))
                        print(response.json().get("message"))
                        
                    except Exception or HTTPError as err:
                        # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                        print ('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))


                    ### no free server selected so ignore the sim post request
                    if (selected_server is None):
                        # wait
                        print(f'runscript sleep {sleeptime} sec at {datetime.now()}')
                        time.sleep(sleeptime)
                        continue
                    
                    
                    ### --- --- --- --- --- --- --- --- sim --- --- --- --- --- --- --- --- 
                    # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                    rootfileinmem = BytesIO()
                    with zipfile.ZipFile(mode='w', file=rootfileinmem, compression = zipfile.ZIP_DEFLATED) as myzip:
                        for root, dirs, files in os.walk(rootfilefolderpath):
                            for file in files:
                                myzip.write(os.path.join(root, file), 
                                            os.path.relpath(os.path.join(root, file), 
                                                            os.path.join(rootfilefolderpath, '..')))
                                # print("filename: ", os.path.join(root, file))
              
                    # 2 write to zip file in local hard disc and zip all files and sub folder in a folder dir     
                    # zippedrootfilename= f'{os.path.basename(rootfilefolderpath)}.zip'
                    # zipf = zipfile.ZipFile(zippedrootfilename, 'w', zipfile.ZIP_DEFLATED)
                    # zipdir( rootfilefolderpath, zipf)
                    # with open(zippedrootfilename, 'rb') as rootfilezip:
                    #     binrootcontent = rootfilezip.read()
                    # # exec(binrootcontent)
                    # rootfilezip.close()
                    
                    try:
                        ### --- --- --- --- post task rootfile to apps server --- --- --- --- 
                        response = requests.post(
                            url = "http://"+ selected_server+ "/runsim?jobid=%d&jobname=%s"\
                                %(jobid, casename), 
                                data= rootfileinmem.getvalue(),
                                headers = binheaders)

                        if response.status_code == 200:
                            jobid = response.json().get("jobid")
                            # logger.info('taskid %d - jobid %d - %s : job rootfile Sent out Successfully! '%(taskid, jobid, datetime.now()))
                            print('taskid %d - jobid %d - %s : rootfile Sent out Successfully!'%(taskid, jobid, datetime.now()))
                            # os.remove(zippedrootfilename)
                            sim_sent_Flag= True
                        elif response.status_code == 404:
                            # logger.warning('taskid %d - job - %s : when upload to apps, server not found '%( taskid, datetime.now()))
                            print ('taskid %d - job - %s : data apps server Not Found.'%( taskid, datetime.now()))
                        elif response.status_code == 500:
                            # logger.warning('taskid %d - job - %s - : when upload to apps, error occurs Internal Server Error '%(taskid, datetime.now()))
                            print ('taskid %d - job - %s : Internal Server Error'%(taskid, datetime.now()))
                        else :
                            # logger.warning('taskid %d - job - %s : when upload to apps, error occurs with status code %d '%( taskid, datetime.now(), response.status_code))
                            print ('taskid %d - job - %s : error with status code %d'%(taskid, datetime.now(), response.status_code))

                    except Exception or HTTPError as err:
                        # logger.warning('taskid %d - job - %s : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
                        print ('taskid %d - job - %s : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now()))
            
                    ### sim post request is failed to send out
                    if (sim_sent_Flag == False):
                        ### --- --- --- --- --- --- --- --- loadbalancer --- --- --- --- --- --- --- --- 
                        try:
                            ### need to tell back to the loadbalancer that server is failed of connection
                            response = requests.post(
                                url = "http://"+ Lb_hostname+ "/freejobserver?&jobid=%d&isfree=%d"\
                                    %( jobid, 1), 
                                    headers = jsheaders)

                            if response.status_code == 200:
                                # logger.info('taskid %d - jobid %d - %s : %s server connection failed ! '%(taskid, jobid, datetime.now(), selected_server))
                                print('taskid %d - jobid %d - %s : %s server connection failed ! '%(taskid, jobid, datetime.now(), selected_server))
                            elif response.status_code == 404:
                                # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, server not found '%( taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %s : loadbalancer server Not Found.'%( taskid, jobid, datetime.now()))
                            elif response.status_code == 500:
                                ### selected_server should be = None
                                selected_server = response.json().get("hostname")
                                # logger.warning('taskid %d - jobid %d - %s - : when connect to loadbalancer, error occurs Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %s : Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                            else :
                                # logger.warning('taskid %d - jobid %d - %s : when upload to loadbalancer, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                                print ('taskid %d - jobid %d - %s : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))
                            
                            ### message from loadbalancer
                            # logger.info(response.json().get("message"))
                            print(response.json().get("message"))
                            
                        except Exception or HTTPError as err:
                            # logger.warning('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                            print ('taskid %d - jobid %d - %s : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
                    
                    
                    # wait
                    print(f'job upload process sleep {sleeptime} sec')
                    time.sleep(sleeptime)

            ### all pop sent out for sim 
            else:
                # ### check how many pop left to be updated its eval
                # print("self.getRemainingRunCaseNum(): ", self.getRemainingRunCaseNum(), "number left in curgen %d at %s"%(cur_gen, datetime.now()))

                while len(self.popjobid_dict)>0:
                    for tId in list(self.popjobid_dict.keys()) :

                        try:
                            jobid = int(self.popjobid_dict[tId])
                            response = requests.get(
                                url = "http://"+ Storage_hostname + "/jobresult?jobid=%d"%(jobid),
                                    headers = jsheaders)

                            if response.status_code == 200:
                                content = response.content
                                
                                inputio = BytesIO(content)

                                jobfolderPath = os.path.join(currentPath, "tmp", casename)
                                ###  1 unzip zipall rootfile from memory bytes to local hard disc
                                inputio.seek(0)
                                with zipfile.ZipFile(file=inputio, mode='r') as inputzipbin:
                                    inputzipbin.extractall(jobfolderPath)

                                AllFileDirNames = find_AlldirInThisFile(jobfolderPath)
                                results_FileDirname= 'results'
                                for FileDirNames in AllFileDirNames:
                                    if re.findall(r"(results$)", FileDirNames):
                                        results_FileDirname = FileDirNames
                                resultfolderPath = os.path.join(jobfolderPath, results_FileDirname)


                                n_dbs = glob.glob(f'{resultfolderPath}/*.db')

                                total_thruput = 0
                                for n_dbPath in n_dbs:

                                    # Create a SQL connection to our SQLite database
                                    con = sqlite3.connect(n_dbPath)

                                    # creating cursor
                                    cur = con.cursor()

                                    # # reading all table names
                                    # table_list = [a for a in cur.execute(
                                    #     "SELECT OBJECT_ID, VEHS FROM DATACOLLECTIONMEASUREMENT_EvaluationTimeIntervalClass WHERE type = 'VEHS' ORDER BY OBJECT_ID ASC;"
                                    #     )]

                                    vehs_ls = [a for a in cur.execute(
                                        "SELECT OBJECT_ID, VEHS FROM DATACOLLECTIONMEASUREMENT_EvaluationTimeIntervalClass ORDER BY OBJECT_ID ASC;"
                                        )]

                                    # print("vehs_ls: ", vehs_ls)



                                    for n in range(len(vehs_ls)):
                                        if int(vehs_ls[n][0]) in AlldictsFromReferenceTable[3].keys():
                                            if "-" in AlldictsFromReferenceTable[3][int(vehs_ls[n][0])] :
                                                side, direction = AlldictsFromReferenceTable[3][int(vehs_ls[n][0])].split("-")
                                            else :
                                                side, direction = AlldictsFromReferenceTable[3][int(vehs_ls[n][0])],None
                                            
                                            # print("vehs_ls id: ", int(vehs_ls[n][0]), type(vehs_ls[n][0]),"vehs_ls vehnum: ",vehs_ls[n][1], type(vehs_ls[n][1]))
                                            # print(side, direction)
                                            if direction == "Exit":
                                                total_thruput += vehs_ls[n][1]
                                            # print("total_thruput: ", total_thruput)

                                    con.close()

                                thruput_per_gene = total_thruput/len(n_dbs)
                                # print(f"thruput_per_gene {thruput_per_gene} of {tId} pop id: ")
                                
                                if (thruput_per_gene > besteval):
                                    bestgenejobid = self.popjobid_dict[tId]
                                    besteval = thruput_per_gene
                                
                                
                                eval = 100000-thruput_per_gene
                                # print(f"eval {eval} of {tId} pop id: ")
                                
                                
                                if (eval != None):
                                        # logger.info('taskid %d - jobid %d - %s : eval update Successfully! '%(taskid, jobid, datetime.now()))
                                    print('taskid %d - jobid %d - %s : eval %f update Successfully!'%(taskid, jobid, datetime.now(), eval))

                                    # # should no throw, getRemainingRunCaseNum()-- iff caseId && evalValue are valid
                                    self.setEvalValue(tId, eval)
                                    del self.popjobid_dict[tId]
                                    ### del all sig from initial seed in taskrootfile
                                    shutil.rmtree(jobfolderPath)

                            elif response.status_code == 404:
                                # logger.warning('taskid %d - jobid %d - %s : when getting value from storage, server not found '%( taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %s : data storage server Not Found.'%( taskid, jobid, datetime.now()))
                            elif response.status_code == 500:
                                # logger.warning('taskid %d - jobid %d - %s - : when  getting value from storage, error occurs Internal Server Error '%(taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %s : Internal Server Error'%(taskid, jobid, datetime.now()))
                            else :
                                # logger.warning('taskid %d - jobid %d - %s : when getting value from storage, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                                print ('taskid %d - jobid %d - %s : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))

                        except Exception or HTTPError as err:
                            # logger.warning('taskid %d - jobid %d - %s : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
                            print ('taskid %d - jobid %d - %s : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))


                    
                    if (len(self.popjobid_dict) == 0 ):   ####　and self.getRemainingRunCaseNum()==0
                        # ###  SGA setting
                        # ### update the gen and subgen for next iteration
                        # if (cur_subgen == numOfsubGen):
                        #     cur_gen += 1
                        #     cur_subgen = 1
                        # else:
                        #     cur_subgen += 1
                        # break
                    
                        # ###  NGA setting
                        cur_gen += 1
                        ## break the while loop in updating eval 
                        break
                    else:
                        # wait for eval update
                        print(f'job upload process sleep {sleeptime} sec')
                        time.sleep(sleeptime)
                        
                ## break the while loop in this curgen 
                break  



def DemandChange(vissimFilePath, rate, timeperiod= "AM"):
    ## vissimFilePath = rootfilefolderpath ## eg.'C:\\Users\\User\\Documents\\temp transfer\\temp\\LungFuRd_newLayout 2022-01-28 (AM)(HwD)(wSig)(AC2)\\' #to be updated
    # Demandrate=1  # Change this rate to apply multiplication factor

    if (timeperiod == "AM"):
        VissimDemandRouting_LungFuRd.applyDmdAMPeak(vissimFilePath, rate)
    elif (timeperiod == "PM"):
        VissimDemandRouting_LungFuRd.applyDmdPMPeak(vissimFilePath, rate)
    
def main():
    global taskid, bestgenejobid, besteval
    
    if ("(AM)" in rootfilefolderpath ):
        DemandChange(rootfilefolderpath , Demandrate, timeperiod="AM")
        print(f"Demand in {rootfilefolderpath} had altered with rate {Demandrate}")
    elif ("(PM)" in rootfilefolderpath ):
        DemandChange(rootfilefolderpath , Demandrate, timeperiod="PM")
        print(f"Demand in {rootfilefolderpath} had altered with rate {Demandrate}")
        
    
    ### --- --- --- --- --- --- --- --- rootfile --- --- --- --- --- --- --- --- 
    AllFileDirNames = find_AlldirInThisFile(rootfilefolderpath)
    print(AllFileDirNames)
    results_FileDirname= 'results'
    for FileDirNames in AllFileDirNames:
        if re.findall(r"(results$)", FileDirNames):
            results_FileDirname = FileDirNames
            
    resultfolderPath = os.path.join(rootfilefolderpath, results_FileDirname)
    ### delete all results
    for root, dirs, files in os.walk(resultfolderPath):
        for file in files:
            os.remove(os.path.join(root, file))
                
    # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
    rootfileinmem = BytesIO()
    with zipfile.ZipFile(mode='w', file=rootfileinmem, compression = zipfile.ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(rootfilefolderpath):
            for file in files:
                myzip.write(os.path.join(root, file), 
                            os.path.relpath(os.path.join(root, file), 
                                            os.path.join(rootfilefolderpath, '..')))
                # print("filename: ", os.path.join(root, file))

    # # 2 write to zip file in local hard disc and zip all files and sub folder in a folder dir     
    # ### zip the rootfile
    # zippedrootfilename= f'{os.path.basename(rootfilefolderpath)}.zip'
    # zipf = zipfile.ZipFile(zippedrootfilename, 'w', zipfile.ZIP_DEFLATED)
    # zipdir( rootfilefolderpath, zipf)
    # with open(zippedrootfilename, 'rb') as rootfilezip:
    #     binrootcontent = rootfilezip.read()
    # # exec(binrootcontent)
    # rootfilezip.close()
    
    # try:
    ### --- --- --- --- post task rootfile to storage server --- --- --- --- 
    response = requests.post(
        url = "http://"+ Storage_hostname+ "/taskrootfile?name=%s&locationid=%d&typeid=%d"\
            %(casename, locationid, typeid), 
            data= rootfileinmem.getvalue(),
            headers = binheaders)

    try:
        if response.status_code == 200:
            taskid = response.json().get("taskid")
            # logger.info('taskid %d - %s : task rootfile Sent out Successfully! '%(taskid, datetime.now()))
            print('taskid %d - %s : task rootfile Sent out Successfully!'%(taskid, datetime.now()))
            # os.remove(zippedrootfilename)
        elif response.status_code == 404:
            # logger.warning('task - %s : when upload to storage, server not found '%( datetime.now()))
            raise ('task - %s : data storage server Not Found.'%( datetime.now()))
        elif response.status_code == 500:
            # logger.warning('task - %s - : when upload to storage, error occurs Internal Server Error '%(datetime.now()))
            raise ('task - %s : Internal Server Error'%(datetime.now()))
        else :
            # logger.warning('task - %s : when upload to storage, error occurs with status code %d '%( datetime.now(), response.status_code))
            raise ('task - %s : error with status code %d'%(datetime.now(), response.status_code))

    except Exception or HTTPError as err:
        # logger.warning('task - %s : when upload to storage, Nonetype unknown error occurs'%( datetime.now())) 
        raise ('task - %s : when upload to storage, Nonetype unknown error occurs'%( datetime.now()))

    

    holder = DISCO2_PyModule_Vissim.Holder()
    holder.loadTdSigData(TdSigpath)    ### <--- change input here
    
    # put in the override class
    runnerVissim = implVissimRunner()
    holder.setVissimRunner(runnerVissim)
    holder.setUseCustomRunner(True)
    
    holder.clearSigFilePath()
    # for sig in sigsBasenames:
    #     holder.addSigFilePath(1, os.path.join(rootfilefolderpath, sig))        ### <--- change input here
    holder.addSigFilePath(0, os.path.join( os.path.join(rootfilefolderpath, 'sig'), "LungFuRd_Roundabout.sig") )        ### <--- change input here
    holder.addSigFilePath(1, os.path.join( os.path.join(rootfilefolderpath, 'sig'), "LungFuRd2.sig") )        ### <--- change input here


    excludeList = DISCO2_PyModule_Vissim.vecInt()
    excludeList[:] = []
    holder.initGA(1, excludeList)


    holder.setGASigInitialCycleTime(0, 50)
    holder.setGASigInitialCycleTime(1, 50)
    # holder.setGASigAllPhaseTimeChangeable(6860, False)
    # holder.setGASigAllPhaseTimeChangeable(6863, False)
    holder.setGASigCycleTimeChangeableInterval(0,10)
    holder.setGASigCycleTimeChangeableInterval(1,10)
    # holder.setGASigCycleTimeChangeable(0,False)
    holder.setGASigOffsetChangeable(0,False)
    holder.setGASigMatchCycleTime(True)
    
    
    # newPlanId = holder.runSGA(
    #     withCycOnlyGen = True, 
    #     numOfGen = numOfGen, 
    #     numOfsubGen = numOfsubGen,
    #     popSize = popSize)    ### <--- change input here

    newPlanId = holder.runGA(
        numOfGen = numOfGen, 
        popSize = popSize)    ### <--- change input here


def get_bestgene(casename, taskid, jobid, eval):
    try:
        response = requests.get(
            url = "http://"+ Storage_hostname + "/jobresult?jobid=%d"%(jobid),
                headers = jsheaders)

        if response.status_code == 200:
            content = response.content
            
            inputio = BytesIO(content)

            ###  1 unzip zipall rootfile from memory bytes to local hard disc
            inputio.seek(0)
            with zipfile.ZipFile(file=inputio, mode='r') as inputzipbin:
                inputzipbin.extractall(os.path.join(currentPath, f'results_taskid={taskid}_jobid={jobid}_thruput={eval}_{casename}'))

        elif response.status_code == 404:
            # logger.warning('taskid %d - jobid %d - %s : when getting value from storage, server not found '%( taskid, jobid, datetime.now()))
            print ('taskid %d - jobid %d - %s : data storage server Not Found.'%( taskid, jobid, datetime.now()))
        elif response.status_code == 500:
            # logger.warning('taskid %d - jobid %d - %s - : when  getting value from storage, error occurs Internal Server Error '%(taskid, jobid, datetime.now()))
            print ('taskid %d - jobid %d - %s : Internal Server Error'%(taskid, jobid, datetime.now()))
        else :
            # logger.warning('taskid %d - jobid %d - %s : when getting value from storage, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
            print ('taskid %d - jobid %d - %s : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))

    except Exception or HTTPError as err:
        # logger.warning('taskid %d - jobid %d - %s : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
        print ('taskid %d - jobid %d - %s : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))



if __name__ == '__main__':
    main()
    get_bestgene(casename= casename, taskid = taskid, jobid = bestgenejobid, eval= besteval)
    
    try:
        print('run')
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping running")
        sys.exit(1)
        
        
        
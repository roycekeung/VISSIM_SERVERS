

from config import *
from variables import *

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

### logging format setup for tracking run history
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(
    filename='runlog.log', 
    level=logging.DEBUG, 
    format=FORMAT,
    datefmt='%m-%d %H:%M',
    filemode='w')
logger = logging.getLogger(__name__)
    
### --- --- --- --- --- --- --- --- cutomized inputs --- --- --- --- --- --- --- --- 
casename = "PokOiVissim 2021-05-05A (Scn 3a) (26AM) 7SGA2" #'{}'.format(random.randint(0,10000))  ### <--- change input here   ### eg. PokOiVissim 2021-05-05A (Scn 3a) (26AM) 7
locationid = LocationEnum.KaiLeng    ### <--- change input here
typeid = AlgoTypeEnum.SGA    ### <--- change input here

ServSelectAlgo = LoadbalancerAlgo.roundrobin    ### <--- change input here
Lbmaxpool = 3

rootfilefolderpath = r"D:\HKUST\VISSIM_SERVERS\runscript\PokOiVissim 2021-05-05A (Scn 3a) (26AM) 7SGA2"     ### <--- change input here
TdSigpath = r"D:\HKUST\VISSIM_SERVERS\runscript\PokOiVissim 2021-05-05A (Scn 3a) (26AM) 7SGA2\pokOi_Scn3a_TdSigData.xml"   ### <--- change input here
sigsBasenames = glob.glob(os.path.join(rootfilefolderpath,'*.sig'))    ### ls gen auto


numOfGen = 3   ### <--- change input here
numOfsubGen = 2   ### <--- change input here
popSize = 10   ### <--- change input here

cur_gen = 1
cur_subgen = 1

taskid = 1

### --- --- --- --- --- --- --- --- prepare global variables naming --- --- --- --- --- --- --- --- 
## host
Lb_hostname = LOADBAL_SERVER[0]
Storage_hostname = STORAGE_SERVER[0]
## header
binheaders = {'Content-type': 'application/octet-stream', 'Connection':'close'}
jsheaders = {'Content-type': 'application/json', 'Connection':'close'}

sleeptime = 3


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


import DISCO2_PyModule_Vissim
# implement override class
class implVissimRunner(DISCO2_PyModule_Vissim.Runner_VissimAsync):

    popjobid_dict = dict()    ## key : tId(popid) ; value : jobid
    
    
    cur_gen = 1
    cur_subgen = 1
    
    # called per (sub)generation, must complete all cases at method return
    def pyRunAll(self):
        global cur_gen, cur_subgen, taskid
        
        while True:
            # returns the count of cases that have not had its eval value set
            # n = self.getRemainingRunCaseNum()
            # relies on TDSigConvertor Vissim sig file mappings, will always modify the same files
            tId = self.makeNextSigFiles()
            
            ### tId ==-1 means stop no more gene
            if (tId >= 0 ):    ### and n > 0
                
                ### --- --- --- --- --- --- --- --- sig --- --- --- --- --- --- --- --- 
                # 1 write bytes to zip file in memory and zip all files and sub folder in a folder dir
                sig_FileBasenames = glob.glob(os.path.join(rootfilefolderpath,'*.sig'))
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
                        # logger.info('taskid %d - jobid %d - %r : job sig Sent out Successfully! '%(taskid, jobid, datetime.now()))
                        print('taskid %d - jobid %d - %r : job sig Sent out Successfully!'%(taskid, jobid, datetime.now()))
                        self.popjobid_dict[f'{tId}'] = jobid
                    elif response.status_code == 404:
                        # logger.warning('taskid %d - job - %r : when upload to storage, server not found '%( taskid, datetime.now()))
                        raise ('taskid %d - job - %r : data storage server Not Found.'%( taskid, datetime.now()))
                    elif response.status_code == 500:
                        # logger.warning('taskid %d - job - %r - : when upload to storage, error occurs Internal Server Error '%(taskid, datetime.now()))
                        raise ('taskid %d - job - %r : Internal Server Error'%(taskid, datetime.now()))
                    else :
                        # logger.warning('taskid %d - job - %r : when upload to storage, error occurs with status code %d '%( taskid, datetime.now(), response.status_code))
                        raise ('taskid %d - job - %r : error with status code %d'%(taskid, datetime.now(), response.status_code))

                except Exception or HTTPError as err:
                    # logger.warning('taskid %d - job - %r : when upload to storage, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
                    raise ('taskid %d - job - %r : when upload to storage, Nonetype unknown error occurs'%(taskid,  datetime.now()))


                
                selected_server =None
                sim_sent_Flag = False
                while selected_server is None and sim_sent_Flag is False:
                    ### --- --- --- --- --- --- --- --- loadbalancer --- --- --- --- --- --- --- --- 
                    try:
                        ### --- --- --- --- ask loadbalancer server for free app server --- --- --- --- 
                        response = requests.post(
                            url = "http://"+ Lb_hostname+ "/selectserver?taskid=%d&jobid=%d&algo=%d&maxpool=%d"\
                                %(taskid, jobid, ServSelectAlgo, Lbmaxpool), 
                                headers = jsheaders)

                        if response.status_code == 200:
                            selected_server = response.json().get("hostname")
                            # logger.info('taskid %d - jobid %d - %r : %s server selected ! '%(taskid, jobid, datetime.now(), selected_server))
                            print('taskid %d - jobid %d - %r : %s server selected ! '%(taskid, jobid, datetime.now(), selected_server))
                        elif response.status_code == 404:
                            # logger.warning('taskid %d - jobid %d - %r : when connect to loadbalancer, server not found '%( taskid, jobid, datetime.now()))
                            print ('taskid %d - jobid %d - %r : loadbalancer server Not Found.'%( taskid, jobid, datetime.now()))
                        elif response.status_code == 500:
                            ### selected_server should be = None
                            selected_server = response.json().get("hostname")
                            # logger.warning('taskid %d - jobid %d - %r - : when connect to loadbalancer, error occurs Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                            print ('taskid %d - jobid %d - %r : Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                        else :
                            # logger.warning('taskid %d - jobid %d - %r : when upload to loadbalancer, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                            print ('taskid %d - jobid %d - %r : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))
                        
                        ### message from loadbalancer
                        # logger.info(response.json().get("message"))
                        print(response.json().get("message"))
                        
                    except Exception or HTTPError as err:
                        # logger.warning('taskid %d - jobid %d - %r : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                        print ('taskid %d - jobid %d - %r : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))


                    ### no free server selected so ignore the sim post request
                    if (selected_server is None):
                        # wait
                        print(f'runscript sleep {sleeptime} sec')
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
                            # logger.info('taskid %d - jobid %d - %r : job rootfile Sent out Successfully! '%(taskid, jobid, datetime.now()))
                            print('taskid %d - jobid %d - %r : rootfile Sent out Successfully!'%(taskid, jobid, datetime.now()))
                            # os.remove(zippedrootfilename)
                            sim_sent_Flag= True
                        elif response.status_code == 404:
                            # logger.warning('taskid %d - job - %r : when upload to apps, server not found '%( taskid, datetime.now()))
                            print ('taskid %d - job - %r : data apps server Not Found.'%( taskid, datetime.now()))
                        elif response.status_code == 500:
                            # logger.warning('taskid %d - job - %r - : when upload to apps, error occurs Internal Server Error '%(taskid, datetime.now()))
                            print ('taskid %d - job - %r : Internal Server Error'%(taskid, datetime.now()))
                        else :
                            # logger.warning('taskid %d - job - %r : when upload to apps, error occurs with status code %d '%( taskid, datetime.now(), response.status_code))
                            print ('taskid %d - job - %r : error with status code %d'%(taskid, datetime.now(), response.status_code))

                    except Exception or HTTPError as err:
                        # logger.warning('taskid %d - job - %r : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now())) 
                        print ('taskid %d - job - %r : when upload to apps, Nonetype unknown error occurs'%(taskid,  datetime.now()))
            
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
                                # logger.info('taskid %d - jobid %d - %r : %s server connection failed ! '%(taskid, jobid, datetime.now(), selected_server))
                                print('taskid %d - jobid %d - %r : %s server connection failed ! '%(taskid, jobid, datetime.now(), selected_server))
                            elif response.status_code == 404:
                                # logger.warning('taskid %d - jobid %d - %r : when connect to loadbalancer, server not found '%( taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %r : loadbalancer server Not Found.'%( taskid, jobid, datetime.now()))
                            elif response.status_code == 500:
                                ### selected_server should be = None
                                selected_server = response.json().get("hostname")
                                # logger.warning('taskid %d - jobid %d - %r - : when connect to loadbalancer, error occurs Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %r : Internal Server Error, no free app server available'%(taskid, jobid, datetime.now()))
                            else :
                                # logger.warning('taskid %d - jobid %d - %r : when upload to loadbalancer, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                                print ('taskid %d - jobid %d - %r : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))
                            
                            ### message from loadbalancer
                            # logger.info(response.json().get("message"))
                            print(response.json().get("message"))
                            
                        except Exception or HTTPError as err:
                            # logger.warning('taskid %d - jobid %d - %r : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                            print ('taskid %d - jobid %d - %r : when connect to loadbalancer, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
                    
                    
                    # wait
                    print(f'job upload process sleep {sleeptime} sec')
                    time.sleep(sleeptime)

            ### all pop sent out for sim 
            else:
                while len(self.popjobid_dict)>0:
                    for tId in self.popjobid_dict.keys():
                        try:
                            ### --- --- --- --- get job eval from storage server and update back to DISCO2_PyModule_Vissim --- --- --- --- 
                            response = requests.get(
                                url = "http://"+ Storage_hostname+ "/jobeval?jobid=%d"\
                                    %(self.popjobid_dict[tId]),
                                    headers = jsheaders)

                            if response.status_code == 200:
                                eval = response.json().get("eval")
                                # logger.info('taskid %d - jobid %d - %r : eval update Successfully! '%(taskid, jobid, datetime.now()))
                                print('taskid %d - jobid %d - %r : eval update Successfully!'%(taskid, jobid, datetime.now()))
                           
                                # should no throw, getRemainingRunCaseNum()-- iff caseId && evalValue are valid
                                self.setEvalValue(tId, eval)
                
                                del self.popjobid_dict[tId]
                            elif response.status_code == 404:
                                # logger.warning('taskid %d - jobid %d - %r : when getting value from storage, server not found '%( taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %r : data storage server Not Found.'%( taskid, jobid, datetime.now()))
                            elif response.status_code == 500:
                                # logger.warning('taskid %d - jobid %d - %r - : when  getting value from storage, error occurs Internal Server Error '%(taskid, jobid, datetime.now()))
                                print ('taskid %d - jobid %d - %r : Internal Server Error'%(taskid, jobid, datetime.now()))
                            else :
                                # logger.warning('taskid %d - jobid %d - %r : when getting value from storage, error occurs with status code %d '%( taskid, jobid, datetime.now(), response.status_code))
                                print ('taskid %d - jobid %d - %r : error with status code %d'%(taskid, jobid, datetime.now(), response.status_code))

                        except Exception or HTTPError as err:
                            # logger.warning('taskid %d - jobid %d - %r : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now())) 
                            print ('taskid %d - jobid %d - %r : when  getting value from storage, Nonetype unknown error occurs'%(taskid, jobid, datetime.now()))
                    
                    if (len(self.popjobid_dict) == 0 ):     ####　and self.getRemainingRunCaseNum()==0
                        ### update the gen and subgen for next iteration
                        if (cur_subgen == numOfsubGen):
                            cur_gen += 1
                            cur_subgen = 1
                        else:
                            cur_subgen += 1
                        break
                    else:
                        # wait for eval update
                        print(f'job upload process sleep {sleeptime} sec')
                        time.sleep(sleeptime)
                        





def main():
    global taskid
    ### --- --- --- --- --- --- --- --- rootfile --- --- --- --- --- --- --- --- 
    AllFileDirNames = find_AlldirInThisFile(rootfilefolderpath)
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
            # logger.info('taskid %d - %r : task rootfile Sent out Successfully! '%(taskid, datetime.now()))
            print('taskid %d - %r : task rootfile Sent out Successfully!'%(taskid, datetime.now()))
            # os.remove(zippedrootfilename)
        elif response.status_code == 404:
            # logger.warning('task - %r : when upload to storage, server not found '%( datetime.now()))
            raise ('task - %r : data storage server Not Found.'%( datetime.now()))
        elif response.status_code == 500:
            # logger.warning('task - %r - : when upload to storage, error occurs Internal Server Error '%(datetime.now()))
            raise ('task - %r : Internal Server Error'%(datetime.now()))
        else :
            # logger.warning('task - %r : when upload to storage, error occurs with status code %d '%( datetime.now(), response.status_code))
            raise ('task - %r : error with status code %d'%(datetime.now(), response.status_code))

    except Exception or HTTPError as err:
        # logger.warning('task - %r : when upload to storage, Nonetype unknown error occurs'%( datetime.now())) 
        raise ('task - %r : when upload to storage, Nonetype unknown error occurs'%( datetime.now()))

    

    holder = DISCO2_PyModule_Vissim.Holder()
    holder.loadTdSigData(TdSigpath)    ### <--- change input here
    holder.clearSigFilePath()
    for sig in sigsBasenames:
        holder.addSigFilePath(1, os.path.join(rootfilefolderpath, sig))        ### <--- change input here
    # holder.addSigFilePAth("PokOi2.sig")        ### <--- change input here

    # put in the override class
    runnerVissim = implVissimRunner()
    holder.setVissimRunner(runnerVissim)
    holder.setUseCustomRunner(True)

    excludeList = DISCO2_PyModule_Vissim.vecInt()
    excludeList[:] = []
    holder.initGA(0, excludeList)

    newPlanId = holder.runSGA(
        withCycOnlyGen = True, 
        numOfGen = numOfGen, 
        numOfsubGen = numOfsubGen,
        popSize = popSize)    ### <--- change input here

    # newPlanId = holder.runGA(
    #     numOfGen = numOfGen, 
    #     popSize = popSize)    ### <--- change input here



if __name__ == '__main__':
    main()
    
    try:
        print('run')
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping running")
        sys.exit(1)
        
        
        
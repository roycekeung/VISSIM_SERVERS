

# receiver
#!/usr/bin/env python
import pika, sys, os
from config import *
import requests
from requests.exceptions import HTTPError
import json
import logging
from datetime import datetime
import base64

def main():

    FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
    logging.basicConfig(filename='quelog.log', level=logging.INFO, format=FORMAT)
    logger = logging.getLogger(__name__)
    
    credentials = pika.PlainCredentials(username='vissim_outputque', password='123456')
    
    ## default usually RabbitMQ will listen on port=5676 or port=5672
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=QUE_SERVER,
            port=5672,
            virtual_host='/',
            credentials=credentials,
            socket_timeout=10,
            blocked_connection_timeout=10,
            connection_attempts=5,
            retry_delay=0.0))
    channel = connection.channel()

    channel.queue_declare(queue='results')
    channel.queue_declare(queue='logs')

    def resultscallback(ch, method, properties, body):
        input_param = json.loads(body)
        
        jobid = input_param['jobid']
        eval = input_param['eval']
        issucceed = 0 if input_param['issucceed']==False or input_param['issucceed']=='False' else 1
        bincontent = base64.b64decode(input_param['content'])
        print("jobid %s results received " % jobid)
        
        ## host
        hostname = STORAGE_SERVER[0]
        ## header
        headers = {'Content-type': 'application/octet-stream', 'Connection':'close'}

        try:
            ### --- --- --- --- post jobresult to storage server --- --- --- --- 
            response = requests.post(
                url = "http://"+ hostname+ "/jobresult?jobid=%d&eval=%f&issucceed=%d"\
                    %(jobid, eval, issucceed), 
                    data= bincontent,
                    headers = headers)

            if response.status_code == 200:
                ### logger.info('jobid %d - %s : Results Sent out Successfully! '%(jobid, datetime.now()))
                print('jobid %d - %s : Results Sent out Successfully!'%(jobid, datetime.now()))
            elif response.status_code == 404:
                ### logger.warning('jobid %d - %s : when upload to storage, server not found '%(jobid, datetime.now()))
                print('jobid %d - %s : data storage server Not Found.'%(jobid, datetime.now()))
            elif response.status_code == 500:
                ### logger.warning('jobid %d - %s - : when upload to storage, error occurs Internal Server Error '%(jobid, datetime.now()))
                print('jobid %d - %s : Internal Server Error'%(jobid, datetime.now()))
            else :
                ### logger.warning('jobid %d - %s : when upload to storage, error occurs with status code %d '%( jobid, datetime.now(), response.status_code))
                print('jobid %d - %s : error with status code %d'%(jobid, datetime.now(), response.status_code))
                
        except Exception or HTTPError as err:
            ### backup result to messagemq tmp
            folderPath = os.path.join(os.getcwd(), 'tmp')
            folderPath = os.path.join(folderPath, 'results')
            folderPath = os.path.join(folderPath, str(jobid))
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
            binary_file_path = os.path.join(folderPath, '%s_eval=%f.zip'%("results",eval)) 
            with open(binary_file_path, 'wb') as f:
                f.write(bincontent)
            ### logger.info('jobid %d - %s : when results backup to messagemq tmp in %s '%(jobid, datetime.now(), binary_file_path))
                
            if (err is not None):
                ### logger.warning('jobid %d - %s : when upload to storage, error occurs %s '%(jobid, datetime.now(), err))
                print('jobid %d - %s : when upload to storage, error occurs %s '%( jobid, datetime.now(),err)) 
            else:
                ### logger.warning('jobid %d - %s : when upload to storage, Nonetype unknown error occurs'%( jobid))
                print('jobid %d - %s : when upload to storage, Nonetype unknown error occurs'%( jobid, datetime.now())) 
       
        try:
            ### --- --- --- --- ask release server thru Loadbalancer --- --- --- --- 
            ## header
            headers = {'Content-type': 'application/json', 'Connection':'close'}
            isfree = 1  
            response = requests.put(
                url = "http://"+ LOADBAL_SERVER[0]+ "/freejobserver?jobid=%d&isfree=%d"%( jobid, isfree), 
                headers= headers
                )
            if response.status_code == 200:
                ### logger.info('jobid %s finished on cal '%jobid)
                print('jobid %d - Success release the app server %s - %s'%(jobid, response.json()["hostname"], datetime.now()))
            elif response.status_code == 404:
                ### logger.error('Loadbalancer server Not Found')
                print('jobid %d - Loadbalancer server Not Found. - %s'%(jobid, datetime.now()))
            elif response.status_code == 408:
                ### logger.warning('Loadbalancer Request Timeout, previous results probably havent been sent out')
                print('jobid %d - '%(jobid), response.get_json()["message"], datetime.now())
            elif response.status_code == 500:
                ### logger.critical(f'Loadbalancer error with status code{response.status_code}')
                print('jobid %d - Internal Loadbalancer Server Error'%jobid, datetime.now())
            else :
                ### logger.error(f'Loadbalancer error with status code{response.status_code}')
                print(f'jobid {jobid} - Loadbalancer error with status code{response.status_code} - {datetime.now()}')
        
        except Exception or HTTPError as err:                
            if (err is not None):
                ### logger.warning('jobid %d - %s : cant release server thru loadbalancer server, error occurs %s '%(jobid, datetime.now(), err))
                print('jobid %d - %s : cant release server thru loadbalancer server %s '%( jobid, datetime.now(),err)) 
            else:
                ### logger.warning('jobid %d - %s :cant release server thru loadbalancer server, Nonetype unknown error occurs'%( jobid))
                print('jobid %d - %s : cant release server thru loadbalancer server, Nonetype unknown error occurs'%( jobid, datetime.now())) 


    def logscallback(ch, method, properties, body):
        input_param = json.loads(body)
        
        jobid = input_param['jobid']
        issucceed = 0 if input_param['issucceed']==False or input_param['issucceed']=='False' else 1
        bincontent = input_param['content']
        iscrashedonvm = input_param['iscrashedonvm']
        print("jobid %s logs received " % jobid)
         
        ## host
        hostname = STORAGE_SERVER[0]
        ## header
        headers = {'Content-type': 'application/json', 'Connection':'close'}

        data = {'log' : bincontent}
        try:
            ### --- --- --- --- post logs to storage server --- --- --- --- 
            response = requests.post(
                url = "http://"+ hostname+ "/joblog?jobid=%d&issucceed=%d"\
                    %(jobid, issucceed), 
                    data= json.dumps(data),
                    headers = headers
                    )

            if response.status_code == 200:
                ### logger.info('jobid %d - %s : Results Sent out Successfully! '%(jobid, datetime.now()))
                print('jobid %d - %s : Results Sent out Successfully!'%(jobid, datetime.now()))
            elif response.status_code == 404:
                ### logger.warning('jobid %d - %s : when upload to storage, server not found '%(jobid, datetime.now()))
                print('jobid %d - %s : data storage server Not Found.'%(jobid, datetime.now()))
            elif response.status_code == 500:
                ### logger.warning('jobid %d - %s - : when upload to storage, error occurs Internal Server Error '%(jobid, datetime.now()))
                print('jobid %d - %s : Internal Server Error'%(jobid, datetime.now()))
            else :
                ### logger.warning('jobid %d - %s : when upload to storage, error occurs with status code %d '%( jobid, datetime.now(), response.status_code))
                print('jobid %d - %s : error with status code %d'%(jobid, datetime.now(), response.status_code))
                
        except Exception or HTTPError as err:
            ### backup result to messagemq tmp
            folderPath = os.path.join(os.getcwd(), 'tmp')
            folderPath = os.path.join(folderPath, 'logs')
            folderPath = os.path.join(folderPath, str(jobid))
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
            binary_file_path = os.path.join(folderPath, '%s.zip'%("logs")) 
            with open(binary_file_path, 'wb') as f:
                f.write(bincontent)
            ### logger.info('jobid %d - %s : when logs backup to messagemq tmp in %s '%(jobid, datetime.now(), binary_file_path))

            if (err is not None):
                ### logger.warning('jobid %d - %s : when upload to storage, error occurs %s '%(jobid, datetime.now(), err))
                print('jobid %d - %s : when upload to storage, error occurs %s '%( jobid, datetime.now(),err)) 
            else:
                ### logger.warning('jobid %d - %s : when upload to storage, Nonetype unknown error occurs'%( jobid, datetime.now()))
                print('jobid %d - %s : when upload to storage, Nonetype unknown error occurs'%( jobid, datetime.now())) 

       
        try:
            if iscrashedonvm == True:
                isfree = 0
            else:
                isfree = 1
                
            ### --- --- --- --- ask release server thru Loadbalancer --- --- --- --- 
            ## header
            headers = {'Content-type': 'application/json', 'Connection':'close'}
             
            response = requests.put(
                url = "http://"+ LOADBAL_SERVER[0]+ "/freejobserver?jobid=%d&isfree=%d"%( jobid, isfree), 
                headers= headers
                )
            if response.status_code == 200:
                ### logger.info('jobid %s finished on cal '%jobid)
                print('jobid %d - Success release the app server %s - %s'%(jobid, response.json()["hostname"], datetime.now()))
            elif response.status_code == 404:
                ### logger.error('Loadbalancer server Not Found')
                print('jobid %d - Loadbalancer server Not Found. - %s'%(jobid, datetime.now()))
            elif response.status_code == 408:
                ### logger.warning('Loadbalancer Request Timeout, previous results probably havent been sent out')
                print('jobid %d - '%(jobid), response.get_json()["message"], datetime.now())
            elif response.status_code == 500:
                ### logger.critical(f'Loadbalancer error with status code{response.status_code}')
                print('jobid %d - Internal Loadbalancer Server Error'%jobid, datetime.now())
            else :
                ### logger.error(f'Loadbalancer error with status code{response.status_code}')
                print(f'jobid {jobid} - Loadbalancer error with status code{response.status_code} - {datetime.now()}')
        
        except Exception or HTTPError as err:                
            if (err is not None):
                ### logger.warning('jobid %d - %s : cant release server thru loadbalancer server, error occurs %s '%(jobid, datetime.now(), err))
                print('jobid %d - %s : cant release server thru loadbalancer server %s '%( jobid, datetime.now(),err)) 
            else:
                ### logger.warning('jobid %d - %s :cant release server thru loadbalancer server, Nonetype unknown error occurs'%( jobid))
                print('jobid %d - %s : cant release server thru loadbalancer server, Nonetype unknown error occurs'%( jobid, datetime.now())) 



    channel.basic_consume(queue='results', on_message_callback=resultscallback, auto_ack=True)
    channel.basic_consume(queue='logs', on_message_callback=logscallback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping message Que")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(0)

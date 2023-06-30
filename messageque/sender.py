# sender
#!/usr/bin/env python
from ast import excepthandler
from logging import exception
import pika
from config import *
import json

credentials = pika.PlainCredentials(username='vissim_outputque', password='123456')


try :
    ### The PERSISTENT_DELIVERY_MODE, which is the default, instructs the JMS provider 
    # to take extra care to ensure that a message is not lost in transit in case of a 
    # JMS provider failure. A message sent with this delivery mode is logged to stable 
    # storage when it is sent
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,  
    )
    mandatory=False
    
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

    results_input = dict()
    results_input['jobid'] = 1
    results_input['issucceed'] = True
    results_input['content'] = "results"
    results = json.dumps(results_input)

    channel.basic_publish(exchange='', routing_key='results', body=results,properties=properties,mandatory=mandatory)
    print(" [x] Sent results")
    # connection.close()

    logs_input = dict()
    logs_input['jobid'] = 2
    logs_input['issucceed'] = False
    logs_input['content'] = "logs"
    logs = json.dumps(logs_input)

    channel.basic_publish(exchange='', routing_key='logs', body=logs,properties=properties,mandatory=mandatory)
    print(" [x] Sent logs")
    # connection.close()


    logs_input = dict()
    logs_input['jobid'] = 3
    logs_input['issucceed'] = False
    logs_input['content'] = "logs2"
    logs = json.dumps(logs_input)

    channel.basic_publish(exchange='', routing_key='logs', body=logs,properties=properties,mandatory=mandatory)
    print(" [x] Sent logs")
    connection.close()
except Exception as err:
    print(f'Other error occurred: server probably not found 404 ; {err}') 




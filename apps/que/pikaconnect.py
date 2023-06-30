# sender
#!/usr/bin/env python
import pika
from app.config import *
import json

credentials = pika.PlainCredentials(username='vissim_outputque', password='123456')

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
print(" [x] output message que is connected")


channel.queue_declare(queue='results')
channel.queue_declare(queue='logs')



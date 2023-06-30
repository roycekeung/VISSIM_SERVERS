Vissim computing scheduler

## Aim:
a distributed computing microservices architecture, using Flask, Rest API, PostgreSQL, Redis, RabbitMQ, Nginx, Socket.IO. Ameliorated the tedious computational iteration by distributing GA optimization jobs of vissim across multiple on-prem, Aws EC2 servers which reduced computational time, eased on horizontal scaling


## Installation:
1. install Redis server v=5.0.14
2. install PostgreSQL 13.0     
    - Server [localhost]: localhost
    - Database [postgres]: vissim_db
    - Port [5432]: 5432
    - Username [postgres]: postgres
    - Password for user postgres: 'mypasword'
3. install erlang 24.0
4. install rabbitmq 3.9.11
5. install docker-compose 1.29.2
6. install docker-desktop 3.4.0

## Host:
1. init storage database dbInitialize.py
2. host app servers for computing  (by docker: >docker-compose up --build)
3. load in available server thru loadin_apapsservers.py
4. host messageque receiver.py  (by docker: >docker-compose up --build)
5. host storage server   (by docker: >docker-compose up --build)
6. host loadbalancer server   (by docker: >docker-compose up --build)
7. customized the runscript to init vissims GA jobs parsing

## NB.
the above server is running under Uvicorn which is an ASGI web server implementation thats ensure a deployable environment
also .env contains the environment variables that should have changed according to each uses so that parse into docker when build


## database:
PostgreSQL, Redis



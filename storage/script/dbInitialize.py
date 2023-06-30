#################################################################################
#
#   Description : - initialize database for user clients and the storage for the 
#                   prerequisite files and the post simulation and optimization files
#                 - format and relationship setup for tables 
#
#################################################################################

import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta 
import time
import os

from sqlalchemy import String, Boolean, Integer, Column, Text, TIMESTAMP, DateTime, CHAR, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from database import Base, SessionLocal, engine, metadata_obj



class LocationEnum(Base):
    __tablename__ = 'vissim_locations'
    
    locationid = Column(Integer, primary_key=True, autoincrement=True)
    locationname = Column(String(128), nullable=False, unique=True)
    createdat = Column(TIMESTAMP , nullable=False)
    updatedat = Column(TIMESTAMP , nullable=False)
    
    tasks = relationship('Task', backref="vissim_locations", uselist=True)

    def __init__(self, locationname):
        ### have to define
        self.locationname = locationname
        self.createdat = datetime.now()
        self.updatedat = datetime.now()

    def __repr__(self):
        return f"<Location locationid={self.locationid} locationname={self.locationname} createdat={self.createdat} updatedat={self.updatedat} >"


class TypeEnum(Base):
    __tablename__ = 'vissim_types'
    
    typeid = Column(Integer, primary_key=True, autoincrement=True)
    typename = Column(String(64), nullable=False, unique=True)
    createdat = Column(TIMESTAMP , nullable=False)
    updatedat = Column(TIMESTAMP , nullable=False)
    
    tasks = relationship('Task', backref="vissim_types", uselist=True)

    def __init__(self, typename):
        ### have to define
        self.typename = typename
        self.createdat = datetime.now()
        self.updatedat = datetime.now()

    def __repr__(self):
        return f"<Type typeid={self.typeid} typename={self.typename} createdat={self.createdat} updatedat={self.updatedat} >"


class Task(Base):
    __tablename__ = 'vissim_tasks'
    
    taskid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=True, unique=True)
    location = Column(Integer, ForeignKey('vissim_locations.locationid'), nullable=True)
    type = Column(Integer, ForeignKey('vissim_types.typeid'), nullable=True)
    rootfile = Column(String(256), nullable=False, unique=True)
    isfinished = Column(Boolean, default=False, nullable=True)
    isrunning = Column(Boolean, default=True, nullable=True)
    createdat = Column(TIMESTAMP , nullable=False)
    updatedat = Column(TIMESTAMP , nullable=False)

    jobs = relationship('Job', backref="vissim_tasks", uselist=True)
    
    def __init__(self, name=None, location=1, type=1, isfinished=None, isrunning=True):
        ### have to define
        self.name = name
        self.location = location
        self.type = type
        self.isfinished = isfinished
        self.isrunning = isrunning        
        self.createdat = datetime.now()
        self.updatedat = datetime.now()

    def __repr__(self):
        return f"<Task name={self.name} rootfile={self.rootfile} createdat={self.createdat} updatedat={self.updatedat} isfinished={self.isfinished} isrunning={self.isrunning}>"
    

class Job(Base):
    __tablename__ = 'vissim_jobs'
    
    jobid = Column(Integer, primary_key=True, autoincrement=True)
    taskid = Column(Integer, ForeignKey('vissim_tasks.taskid'), nullable=True)
    popid = Column(Integer, nullable=False)
    eval = Column(Float, nullable=True)
    gen = Column(Integer, nullable=True, unique=False)
    subgen = Column(Integer, nullable=True, unique=False)
    sig = Column(String(256), nullable=True, unique=True)
    results = Column(String(256), nullable=True, unique=True)
    log =Column(String(640), nullable=True, unique=False)
    issucceed = Column(Boolean, nullable=True)
    createdat = Column(TIMESTAMP , nullable=False)
    updatedat = Column(TIMESTAMP , nullable=False)

    def __init__(self ,popid=1, gen=1, subgen=0, sig= None):
        self.popid = popid
        self.gen = gen
        self.subgen = subgen
        self.sig = sig
        self.createdat = datetime.now()
        self.updatedat = datetime.now()


    def __repr__(self):
        return f"<Job jobid={self.jobid} Job taskid={self.taskid} popid={self.popid} location={self.location} eval={self.eval} sig={self.sig} results={self.results} issucceed={self.issucceed} updatedat={self.updatedat}>"



locations_tb = Table('vissim_locations', metadata_obj,
    Column('locationid', Integer, primary_key=True, autoincrement=True),
    Column('locationname', String(128), nullable=False, unique=True),
    Column('createdat', TIMESTAMP , nullable=False),
    Column('updatedat', TIMESTAMP , nullable=False)
)

types_tb = Table('vissim_types', metadata_obj,
    Column('typeid', Integer, primary_key=True, autoincrement=True),
    Column('typename', String(64), nullable=False, unique=True),
    Column('createdat', TIMESTAMP , nullable=False),
    Column('updatedat', TIMESTAMP , nullable=False)
)

task_tb = Table('vissim_tasks', metadata_obj,
    Column('taskid', Integer, primary_key=True, autoincrement=True),
    Column('name', String(128), nullable=True, unique=True),
    Column('location', Integer, ForeignKey('vissim_locations.locationid'), nullable=True),
    Column('type', Integer, ForeignKey('vissim_types.typeid'), nullable=True),
    Column('rootfile', String(256), nullable=True, unique=True),
    Column('createdat', TIMESTAMP , nullable=False),
    Column('updatedat', TIMESTAMP , nullable=False),
    Column('isfinished', Boolean, default=False, nullable=False),
    Column('isrunning', Boolean, default=True, nullable=False)
)

job_tb = Table('vissim_jobs', metadata_obj,
    Column('jobid', Integer, primary_key=True, autoincrement=True),
    Column('taskid', Integer, ForeignKey('vissim_tasks.taskid'), nullable=True),
    Column('popid', Integer, nullable=False),
    Column('eval', Float, nullable=True),
    Column('gen', Integer, nullable=True, unique=False),
    Column('subgen', Integer, nullable=True, unique=False),
    Column('sig', String(256), nullable=True, unique=True),
    Column('results', String(256), nullable=True, unique=True),
    Column('log', String(640), nullable=True, unique=False),
    Column('issucceed', Boolean, nullable=True),
    Column('createdat', TIMESTAMP , nullable=False),
    Column('updatedat', TIMESTAMP , nullable=False)
)



metadata_obj.create_all(engine)
dbSession = SessionLocal()
dbSession.commit()

try :
    ### --- --- --- add locations --- --- --- 
    Locations_list = []
    loc1 = LocationEnum(locationname='Kai Leng' )
    Locations_list.append(loc1)
    loc2 = LocationEnum(locationname='Kwun Tong')
    Locations_list.append(loc2)
    loc3 = LocationEnum(locationname='Lam Tin' )
    Locations_list.append(loc3)
    loc4 = LocationEnum(locationname='Lung Fung Rd')
    Locations_list.append(loc4)
    
    dbSession.add_all(Locations_list)
    dbSession.commit()
    
    ### --- --- --- add types --- --- --- 
    types_list = []
    type1 = TypeEnum(typename='Calibration' )
    types_list.append(type1)
    type2 = TypeEnum(typename='NGA')
    types_list.append(type2)
    type3 = TypeEnum(typename='SGA')
    types_list.append(type3)
    
    dbSession.add_all(types_list)
    dbSession.commit()
    
    dbSession.flush()

except:
    pass

# try :
#     ### --- --- --- add users --- --- --- 
#     # hash_password = hashlib.sha256(b"123456").hexdigest()
#     password = "123456"

#     users_list = []
#     user1 = User(username='admin@gmail.com', password=password, expireperiod= timedelta(days=30*2) )
#     users_list.append(user1)
#     user2 = User(username='avatartest@gmail.com', password=password, expireperiod= timedelta(days=30*2))
#     users_list.append(user2)

#     dbSession.add_all(users_list)
#     dbSession.commit()


#     ### --- --- --- add storages --- --- --- 
#     os.chdir('../')
#     os.chdir('../')

#     folderPath = os.getcwd()

#     input_folderPath = folderPath + "\\test\\run_inputs\\pfile.binary"

#     input_folderPath2 = folderPath + "\\test\\run_inputs\\pfile2.binary"

#     input_folderPath3 = folderPath + "\\test\\run_inputs\\pfile3.binary"

#     os.chdir("./storage")
#     os.chdir("./script")
#     folderPath = os.getcwd()


#     storages_list = []
#     storage1 = Storage( simoptid=1, type='sim', input= input_folderPath )
#     storage2 = Storage( simoptid=2, type='optnga', input= input_folderPath2)
#     storage3 = Storage( simoptid=1, type='optsga', input= input_folderPath3)
#     user1.storages.append(storage1)
#     user1.storages.append(storage2)
#     user2.storages.append(storage3)

#     dbSession.add_all(storages_list)
#     dbSession.commit()

#     dbSession.flush()
# except:
#     pass





from app import db

from sqlalchemy import String, Boolean, Integer, Column, Text, TIMESTAMP, DateTime, CHAR, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from datetime import datetime, timedelta 

from err.errcollection import *

import hashlib

import logging

logger = logging.getLogger(__name__)

class LocationEnum(db.Model):
    __tablename__ = 'vissim_locations'
    
    locationid = Column(Integer, primary_key=True, autoincrement=True)
    locationname = Column(String(128), nullable=False, unique=True)
    createdat = Column(TIMESTAMP , nullable=False)
    updatedat = Column(TIMESTAMP , nullable=False)
    
    # jobs = relationship("Job", back_populates="vissim_jobs")
    tasks = relationship('Task', backref="vissim_locations", uselist=True)

    def __init__(self, locationname):
        ### have to define
        self.locationname = locationname
        self.createdat = datetime.now()
        self.updatedat = datetime.now()

    
    ### --- --- --- --- --- --- check --- --- --- --- --- --- 
    @staticmethod
    def is_locobj_exist(locname):
        return LocationEnum.query.filter(LocationEnum.locationname == locname).first() is not None

    ### --- --- --- --- --- --- getter --- --- --- --- --- --- 
    @staticmethod
    def get_locobj_by_locid(locid):
        return LocationEnum.query.filter(LocationEnum.locationid == locid).first()
    
    @staticmethod
    def get_locobj_by_locname(locname):
        return LocationEnum.query.filter(LocationEnum.locationname == locname).first()
    
    @staticmethod
    def get_locname_by_locid(locid):
        return LocationEnum.query.filter(LocationEnum.locationid == locid).first().locationname
    
    @staticmethod
    def get_locid_by_locname(locname):
        return LocationEnum.query.filter(LocationEnum.locationname == locname).first().locationid
    
    ### --- --- --- --- --- --- create --- --- --- --- --- --- 
    @staticmethod
    def insert_locobj(locobj):
        if isinstance(locobj, LocationEnum):
            db.session.add(locobj)
            db.session.commit()
            return True
        else:
            return False

    ### --- --- --- --- --- --- set/update --- --- --- --- --- --- 
    @staticmethod
    def update_locobj():
        db.session.commit()

    @staticmethod
    def set_locname_by_locid(locid, locname=None):
        LocationEnum.query.filter(LocationEnum.locationid == locid).update(dict(locationname=locname))
        LocationEnum.query.filter(LocationEnum.locationid == locid).update(dict(updatedat=datetime.now()))
        db.session.commit()
        
    @staticmethod
    def add_task_by_locid(locid , Task):
        tmp = LocationEnum.get_locobj_by_locid(locid)   ### split to avoid garbage collected
        tmp.tasks.append(Task)
        db.session.add(Task)
        db.session.commit()

    @staticmethod
    def add_task_by_locobj(locobj , Task):
        locobj.tasks.append(Task)
        db.session.add(Task)
        db.session.commit()

    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    @staticmethod
    def delete_locobj_by_locid(locid):
        locobj = LocationEnum.query.filter(LocationEnum.location == locid).first()
        if (locobj is not None):
            db.session.delete(LocationEnum.get_locobj_by_locid(locid))
            db.session.commit()
        else:
            logger.error(LocationIsInUseError)
            raise LocationIsInUseError

    
    def __repr__(self):
        return f"<Location locationid={self.locationid} locationname={self.locationname} createdat={self.createdat} updatedat={self.updatedat} >"

class TypeEnum(db.Model):
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

    
    ### --- --- --- --- --- --- check --- --- --- --- --- --- 
    @staticmethod
    def is_type_exist(typename):
        return TypeEnum.query.filter(TypeEnum.typename == typename).first() is not None

    ### --- --- --- --- --- --- getter --- --- --- --- --- --- 
    @staticmethod
    def get_typeobj_by_typeid(typeid):
        return TypeEnum.query.filter(TypeEnum.typeid == typeid).first()
    
    @staticmethod
    def get_typeobj_by_typename(typename):
        return TypeEnum.query.filter(TypeEnum.typename == typename).first()
    
    @staticmethod
    def get_typename_by_typeid(typeid):
        return TypeEnum.query.filter(TypeEnum.typeid == typeid).first().typename
    
    @staticmethod
    def get_typeid_by_typename(typename):
        return TypeEnum.query.filter(TypeEnum.typename == typename).first().typeid
    
    ### --- --- --- --- --- --- create --- --- --- --- --- --- 
    @staticmethod
    def insert_typeobj(typeobj):
        if isinstance(typeobj, TypeEnum):
            db.session.add(typeobj)
            db.session.commit()
            return True
        else:
            return False

    ### --- --- --- --- --- --- set/update --- --- --- --- --- --- 
    @staticmethod
    def update_type():
        db.session.commit()

    @staticmethod
    def set_typename_by_typeid(typeid, typename=None):
        TypeEnum.query.filter(TypeEnum.typeid == typeid).update(dict(typename=typename))
        TypeEnum.query.filter(TypeEnum.typeid == typeid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def add_task_by_typeid(typeid , Task):
        tmp = TypeEnum.get_typeobj_by_typeid(typeid)   ### split to avoid garbage collected
        tmp.tasks.append(Task)
        db.session.add(Task)
        db.session.commit()

    @staticmethod
    def add_task_by_typeobj(typeobj , Task):
        typeobj.tasks.append(Task)
        db.session.add(Task)
        db.session.commit()

    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    @staticmethod
    def delete_typeobj_by_typeid(typeid):
        typeoj = TypeEnum.query.filter(TypeEnum.typeid == typeid).first()
        if (typeoj is not None):
            db.session.delete(TypeEnum.get_typeobj_by_typeid(typeid))
            db.session.commit()
        else:
            logger.error(TypeIsInUseError)
            raise TypeIsInUseError

    
    def __repr__(self):
        return f"<Type typeid={self.typeid} typename={self.typename} createdat={self.createdat} updatedat={self.updatedat} >"


class Task(db.Model):
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
        
    ### --- --- --- --- --- --- check --- --- --- --- --- --- 
    @staticmethod
    def is_task_exist(taskid):
        return Task.query.filter(Task.taskid == taskid).first() is not None
    
    ### --- --- --- --- --- --- getter --- --- --- --- --- --- 
    @property
    def get_taskid(self):
        return self.taskid

    
    @staticmethod
    def get_all_tasks():
        return Task.query.all()
    
    @staticmethod
    def get_running_tasks():
        return Task.query.filter(Task.isrunning == True).all()
    
    @staticmethod
    def get_tasks_by_location(location):
        return Task.query.filter(Task.location == location).all()
    
    @staticmethod
    def get_taskids_by_location(location):
        _taskids = list()
        for _Job in Job.query.filter(Task.location == location).order_by(Task.taskid).all():
            _taskids.append(_Job.taskid)
        # _taskids.sort()
        return _taskids
    
    @staticmethod
    def get_tasknames_by_location(location):
        _tasknames = list()
        for _Job in Job.query.filter(Task.location == location).all():
            _tasknames.append(_Job.name)
        # _tasknames.sort()
        return _tasknames
    
    @staticmethod
    def get_task_by_name(name):
        return Task.query.filter(Task.name == name).first()
    
    @staticmethod
    def get_task_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first()

    @staticmethod
    def get_taskid_by_name(name):
        return Task.query.filter(Task.name == name).first().taskid

    @staticmethod
    def get_name_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().name

    @staticmethod
    def get_locid_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().location

    @staticmethod
    def get_locid_by_name(name):
        return Task.query.filter(Task.name == name).first().location

    @staticmethod
    def get_typeid_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().type

    @staticmethod
    def get_typeid_by_name(name):
        return Task.query.filter(Task.name == name).first().type
    
    # @staticmethod
    # def get_progress_by_name(name):
    #     return "{0:.1f}%".format(Task.query.filter(Task.name == name).first().genenum/Task.query.filter(Task.name == name).first().totalgenenum)

    # @staticmethod
    # def get_progress_by_taskid(taskid):
    #     return "{0:.1f}%".format(Task.query.filter(Task.taskid == taskid).first().genenum/Task.query.filter(Task.taskid == taskid).first().totalgenenum)
    
    @staticmethod
    def get_rootfile_by_name(name):
        return Task.query.filter(Task.name == name).first().rootfile

    @staticmethod
    def get_rootfile_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().rootfile

    @staticmethod
    def is_finished_by_name(name):
        return Task.query.filter(Task.name == name).first().isfinished

    @staticmethod
    def is_finished_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().isfinished

    @staticmethod
    def is_running_by_name(name):
        return Task.query.filter(Task.name == name).first().isrunning

    @staticmethod
    def is_running_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().isrunning

    @staticmethod
    def get_runtime_by_taskid(taskid):
        return Task.query.filter(Task.taskid == taskid).first().updatedat - Task.query.filter(Task.taskid == taskid).first().createdat

    @staticmethod
    def get_runtime_by_name(name):
        return Task.query.filter(Task.name == name).first().updatedat - Task.query.filter(Task.name == name).first().createdat

    ### --- --- --- --- --- --- create --- --- --- --- --- --- 
    @staticmethod
    def insert_task(task):
        if isinstance(task, Task):
            db.session.add(task)
            db.session.commit()
            return True
        else:
            return False

    ### --- --- --- --- --- --- set/update --- --- --- --- --- --- 
    @staticmethod
    def update_task():
        db.session.commit()

    @staticmethod
    def set_name_by_taskid(taskid, name=None):
        Task.query.filter(Task.taskid == taskid).update(dict(name=name))
        Task.query.filter(Task.taskid == taskid).update(dict(updatedat=datetime.now()))
        db.session.commit()
        
    @staticmethod
    def set_rootfile_by_taskid(taskid, rootfile=None):
        Task.query.filter(Task.taskid == taskid).update(dict(rootfile=rootfile))
        Task.query.filter(Task.taskid == taskid).update(dict(updatedat=datetime.now()))
        db.session.commit()
        
    @staticmethod
    def set_rootfile_by_name(name, rootfile=None):
        Task.query.filter(Task.name == name).update(dict(rootfile=rootfile))
        Task.query.filter(Task.name == name).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_finish_by_name(name, bool=True):
        Task.query.filter(Task.name == name).update(dict(isfinished=bool))
        Task.query.filter(Task.name == name).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_finish_by_taskid(taskid, bool=True):
        Task.query.filter(Task.taskid == taskid).update(dict(isfinished=bool))
        Task.query.filter(Task.taskid == taskid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_running_by_name(name, bool=False):
        Task.query.filter(Task.name == name).update(dict(isrunning=bool))
        Task.query.filter(Task.name == name).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_running_by_taskid(taskid, bool=False):
        Task.query.filter(Task.taskid == taskid).update(dict(isrunning=bool))
        Task.query.filter(Task.taskid == taskid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def add_job_by_taskid(taskid , Job):
        tmp = Task.get_task_by_taskid(taskid)   ### split to avoid garbage collected
        tmp.jobs.append(Job)
        db.session.add(Job)
        db.session.commit()

    @staticmethod
    def add_job_by_task(task , Job):
        task.storages.append(Job)
        db.session.add(Job)
        db.session.commit()

    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    @staticmethod
    def delete_task_by_taskid(taskid):
        task = Task.query.filter(Task.taskid == taskid).first()
        if (task.isrunning== False):
            db.session.delete(task)
            db.session.commit()
        else:
            logger.error(TaskisrunningError)
            raise TaskisrunningError


    def __repr__(self):
        return f"<Task name={self.name} rootfile={self.rootfile} createdat={self.createdat} updatedat={self.updatedat} isfinished={self.isfinished} isrunning={self.isrunning}>"


class Job(db.Model):
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


    ### --- --- --- --- --- --- check --- --- --- --- --- --- 
    @staticmethod
    def is_job_exist_by_taskid(taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first() is not None

    @staticmethod
    def is_job_exist_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first() is not None

    @staticmethod
    def is_succeed_by_taskid(taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().issucceed

    @staticmethod
    def is_succeed_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().issucceed
    
    @staticmethod
    def is_succeed_jobls_by_taskid(taskid):
        _issucceedjobidls = Job.get_jobids_by_taskid(taskid) 
        joblsissucceed = []
        for jobid in _issucceedjobidls:
            joblsissucceed.append(Job.is_succeed_by_jobid(jobid))
        # _issucceedjobidls.sort()
        return joblsissucceed
        
    ### --- --- --- --- --- --- getter --- --- --- --- --- --- 
    @property
    def get_jobid(self):
        return self.jobid
    
    @staticmethod
    def get_jobid_by_taskid(taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().jobid
    
    @staticmethod
    def get_jobs_by_taskid(taskid):
        return Job.query.filter(Job.taskid == taskid).all()

    @staticmethod
    def get_jobids_by_taskid(taskid):
        _jobids = list()
        for _Job in Job.query.filter(Job.taskid == taskid).order_by(Job.jobid).all():
            _jobids.append(_Job.jobid)
        # _jobids.sort()
        return _jobids

    @staticmethod
    def get_taskid_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().taskid
    
    @property
    def get_popid(self):
        return self.popid
    
    @staticmethod
    def get_popids_by_taskid(taskid, gen=1, subgen=0):
        _popids = list()
        for _Job in Job.query.filter(Job.taskid == taskid, Job.gen==gen, Job.subgen==subgen).order_by(Job.popid).all():
            _popids.append(_Job.popid)
        # _popids.sort()
        return _popids
    
    @staticmethod
    def get_popid_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().popid

    @classmethod
    def get_eval_by_taskid(cls, taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().eval
    
    @classmethod
    def get_eval_by_jobid(cls, jobid):
        return Job.query.filter(Job.jobid == jobid).first().eval

    @staticmethod
    def get_gen_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().gen

    @staticmethod
    def get_subgen_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().subgen

    @classmethod
    def get_sig_by_taskid(cls, taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().sig

    @classmethod
    def get_sig_by_jobid(cls, jobid):
        return Job.query.filter(Job.jobid == jobid).first().sig

    @classmethod
    def get_result_by_taskid(cls, taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().results

    @classmethod
    def get_result_by_jobid(cls, jobid):
        return Job.query.filter(Job.jobid == jobid).first().results

    @classmethod
    def get_log_by_taskid(cls, taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().log

    @staticmethod
    def get_log_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().log
    
    @staticmethod
    def get_runtime_by_taskid(taskid, popid, gen=1, subgen=0):
        return Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().updatedat \
            - Job.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).first().createdat

    @staticmethod
    def get_runtime_by_jobid(jobid):
        return Job.query.filter(Job.jobid == jobid).first().updatedat - Job.query.filter(Job.jobid == jobid).first().createdat

    @staticmethod
    def get_failed_jobids_by_taskid(taskid, failedtime):
        ## None; no reponse the results get lost
        failed_jobids = Job.query.filter(\
            Job.taskid == taskid, \
            Job.issucceed == None, \
            datetime.now() - Job.updatedat > timedelta(seconds = failedtime)\
                ).order_by(Job.jobid).all()
        
        _jobids = list()
        for _Job in failed_jobids:
            _jobids.append(_Job.jobid)
            
        ## False; received error from app server
        failed_jobids = Job.query.filter(\
            Job.taskid == taskid, \
            Job.issucceed == False
                ).order_by(Job.jobid).all()
        
        for _Job in failed_jobids:
            _jobids.append(_Job.jobid)
        
        return _jobids
        
    ### --- --- --- --- --- --- create --- --- --- --- --- --- 
    @staticmethod
    def insert_job(job):
        if isinstance(job, Job):
            db.session.add(job)
            db.session.commit()
            return True
        else:
            return False

    ### --- --- --- --- --- --- set/update --- --- --- --- --- --- 
    @staticmethod
    def update_job():
        db.session.commit()

    @staticmethod
    def set_popid_by_jobid(jobid, popid):
        Job.query.filter(Job.jobid == jobid).update(dict(popid=popid))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_eval_by_jobid(jobid, eval):
        Job.query.filter(Job.jobid == jobid).update(dict(eval=eval))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_gen_by_jobid(jobid, gen):
        Job.query.filter(Job.jobid == jobid).update(dict(gen=gen))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_subgen_by_jobid(jobid, subgen):
        Job.query.filter(Job.jobid == jobid).update(dict(subgen=subgen))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()
        
    @staticmethod
    def set_sig_by_jobid(jobid, sig):
        Job.query.filter(Job.jobid == jobid).update(dict(sig=sig))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_result_by_jobid(jobid, result):
        Job.query.filter(Job.jobid == jobid).update(dict(results=result))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_log_by_jobid(jobid, log):
        Job.query.filter(Job.jobid == jobid).update(dict(log=log))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()

    @staticmethod
    def set_issucceed_by_jobid(jobid, issucceed):
        Job.query.filter(Job.jobid == jobid).update(dict(issucceed=issucceed))
        Job.query.filter(Job.jobid == jobid).update(dict(updatedat=datetime.now()))
        db.session.commit()


    @staticmethod
    def add_job_by_taskid(taskid , job):
        tmp = Task.get_task_by_taskid(taskid)   ### split to avoid garbage collected
        tmp.jobs.append(job)
        db.session.add(job)
        db.session.commit()

    @staticmethod
    def add_job_by_task(task , job):
        task.jobs.append(job)
        db.session.add(job)
        db.session.commit()
        

    ### --- --- --- --- --- --- delete --- --- --- --- --- --- 
    @staticmethod
    def delete_job_by_taskid(taskid, popid, gen, subgen):
        Task.query.filter(Job.taskid == taskid, Job.popid == popid, Job.gen == gen, Job.subgen == subgen).delete(synchronize_session='evaluate') ## delete row
        db.session.commit()
    
    @staticmethod
    def delete_job_by_jobid(jobid):
        job = Job.query.filter(Job.jobid == jobid).first()
        db.session.delete(job)
        db.session.commit()

    @staticmethod
    def delete_jobs_by_taskid(taskid):
        Task.query.filter(Job.taskid == taskid).delete(synchronize_session='evaluate')  ## delete rows
        db.session.commit()

    @staticmethod
    def delete_jobs_by_name(name):
        task = Task.query.filter(Task.name == name).first()
        Task.query.filter(Job.taskid == task.taskid).delete(synchronize_session='evaluate') ## delete rows
        db.session.commit()

    @staticmethod
    def delete_job(job):
        db.session.delete(job)
        db.session.commit()


    def __repr__(self):
        return f"<Job jobid={self.jobid} Job taskid={self.taskid} popid={self.popid} location={self.location} eval={self.eval} sig={self.sig} results={self.results} issucceed={self.issucceed} updatedat={self.updatedat}>"


# from sqlalchemy import event, DDL

# mine = DDL('''\
# CREATE TRIGGER update_occ() UPDATE OF occ ON Job
#   BEGIN
#     PERFORM pg_notify('occ_updated', new.taskid);
#   END;
#   $$ LANGUAGE plpgsql
# CREATE TRIGGER todos_notify_trig AFTER UPDATE OF occ ON Job EXECUTE PROCEDURE update_occ();
# ''')

# event.listen(Job.__table__, 'after_create', mine)

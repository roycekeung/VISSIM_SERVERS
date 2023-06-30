#################################################################################
#
#   Description : rest API router
#
#################################################################################

import logging.config
from app import api
from app.controller import PingTest, TaskRootfile, JobRootfile, JobEval, JobSigCreate, JobResult, JobSigResult, JobLog, TaskStatus, \
    JobStatus, ResultSum, ResultsSum, TaskJobList, FailedJobList, EndTask

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": "info.log",
                "maxBytes": 10485760,
                "backupCount": 100,
                "encoding": "utf8",
            },
            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "simple",
                "filename": "errors.log",
                "maxBytes": 10485760,
                "backupCount": 70,
                "encoding": "utf8",
            },
            "debug_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "debug.log",
                "maxBytes": 10485760,
                "backupCount": 100,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "my_module": {"level": "ERROR", "handlers": ["console"], "propagate": "no"}
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["error_file_handler", "debug_file_handler"],
        },
    }
)


api.add_resource(PingTest, '/pingtest', resource_class_kwargs={
    'logger': logging.getLogger('/pingtest')
})

api.add_resource(TaskRootfile, '/taskrootfile', resource_class_kwargs={
    'logger': logging.getLogger('/taskrootfile')
})

api.add_resource(JobRootfile, '/jobrootfile', resource_class_kwargs={
    'logger': logging.getLogger('/jobrootfile')
})

api.add_resource(JobEval, '/jobeval', resource_class_kwargs={
    'logger': logging.getLogger('/jobeval')
})

api.add_resource(JobSigCreate, '/jobsigcreate', resource_class_kwargs={
    'logger': logging.getLogger('/jobsigcreate')
})

api.add_resource(JobResult, '/jobresult', resource_class_kwargs={
    'logger': logging.getLogger('/jobresult')
})

# api.add_resource(JobResults, '/jobresults', resource_class_kwargs={
#     'logger': logging.getLogger('/jobresults')
# })

api.add_resource(JobSigResult, '/jobsigresult', resource_class_kwargs={
    'logger': logging.getLogger('/jobsigresult')
})

api.add_resource(JobLog, '/joblog', resource_class_kwargs={
    'logger': logging.getLogger('/joblog')
})

api.add_resource(TaskStatus, '/taskstatus', resource_class_kwargs={
    'logger': logging.getLogger('/taskstatus')
})

api.add_resource(JobStatus, '/jobstatus', resource_class_kwargs={
    'logger': logging.getLogger('/jobstatus')
})

api.add_resource(ResultSum, '/resultsum', resource_class_kwargs={
    'logger': logging.getLogger('/resultsum')
})

api.add_resource(ResultsSum, '/resultssum', resource_class_kwargs={
    'logger': logging.getLogger('/resultssum')
})

api.add_resource(TaskJobList, '/taskjoblist', resource_class_kwargs={
    'logger': logging.getLogger('/taskjoblist')
})

api.add_resource(FailedJobList, '/failedjoblist', resource_class_kwargs={
    'logger': logging.getLogger('/failedjoblist')
})

api.add_resource(EndTask, '/endtask', resource_class_kwargs={
    'logger': logging.getLogger('/endtask')
})

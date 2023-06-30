#################################################################################
#
#   Description : rest API router
#
#################################################################################

import logging.config
from app import api
from app.controller import PingTest, RunSim, RunStat, RunLog, TaskkillCheck

## logging config setting
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

api.add_resource(RunSim, '/runsim', resource_class_kwargs={
    'logger': logging.getLogger('/runsim')
})

api.add_resource(RunStat, '/runstat', resource_class_kwargs={
    'logger': logging.getLogger('/runstat')
})

api.add_resource(RunLog, '/runlog', resource_class_kwargs={
    'logger': logging.getLogger('/runlog')
})

api.add_resource(TaskkillCheck, '/taskkillcheck', resource_class_kwargs={
    'logger': logging.getLogger('/taskkillcheck')
})

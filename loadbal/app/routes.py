#################################################################################
#
#   Description : rest API router
#
#################################################################################

import logging.config
from app import api
from app.controller import SelectServer, FreeJobServer, FreeServer, JobCount, CancelTask, CancelJob, EndTaskRunning

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

api.add_resource(SelectServer, '/selectserver', resource_class_kwargs={
    'logger': logging.getLogger('/selectserver')
})

api.add_resource(FreeJobServer, '/freejobserver', resource_class_kwargs={
    'logger': logging.getLogger('/freejobserver')
})

api.add_resource(FreeServer, '/freeserver', resource_class_kwargs={
    'logger': logging.getLogger('/freeserver')
})

api.add_resource(JobCount, '/jobcount', resource_class_kwargs={
    'logger': logging.getLogger('/jobcount')
})

api.add_resource(CancelTask, '/canceltask', resource_class_kwargs={
    'logger': logging.getLogger('/canceltask')
})

api.add_resource(CancelJob, '/canceljob', resource_class_kwargs={
    'logger': logging.getLogger('/canceljob')
})

api.add_resource(EndTaskRunning, '/endtaskrunning', resource_class_kwargs={
    'logger': logging.getLogger('/endtaskrunning')
})

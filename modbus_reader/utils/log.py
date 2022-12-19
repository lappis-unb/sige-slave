import os

UtilsLog = {
    'disable_existing_loggers': False,
    'formatters': {
        'standard': { 'format': '[%(levelname)s] [%(asctime)s] [%(module)s] -- %(message)s'},
        'error': {'format': '[%(levelname)s] [%(asctime)s] [%(pathname)s] [%(module)s] -- %(message)s'},
        'simple': {'format': '[%(levelname)s] [%(asctime)s] -- %(message)s'},
        'collect': {'format': '%(message)s'}
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',                  
            'class': 'logging.StreamHandler',  
            'formatter': 'simple'           
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(log_path, "default.log"), 
            'when': 'D',
            'interval': 1,
            'backupCount': 30, 
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(log_path, "error.log"),
            'when': 'D',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'error',
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'default', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'collect': {
            'handlers': ['default', 'error'],
            'level': 'INFO',
        }
    },
}

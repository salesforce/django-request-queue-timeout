from logging import Filter

SECRET_KEY = "required but unused setting"
ROOT_URLCONF = "urls"


class DropFilter(Filter):
    def filter(self, record):
        return False


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"testing": {"()": DropFilter}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["testing"],
        }
    },
    "loggers": {
        "rqto.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

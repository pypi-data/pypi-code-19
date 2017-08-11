config = dict(
    logging=dict(
        loggers=dict(
            robosignatory={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
            root={
                "level": "INFO",
                "propagate": False,
                "handlers": ["console"],
            },
        ),
    ),
)

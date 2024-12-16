# TODO: make a config  module
import logging
import logging.config
from .conf_types import BaseConfig, ProductionConfig, DevelopmentConfig, TestingConfig

log_file_path = "clickclickclick.log"
log_level = "DEBUG"

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": log_level,
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": log_file_path,
        },
    },
    "loggers": {
        "clickclickclick.finder": {
            "handlers": ["console", "file"],
            "level": log_level,
            "propagate": True,
        },
        "clickclickclick.executor": {
            "handlers": ["console", "file"],
            "level": log_level,
            "propagate": True,
        },
        "clickclickclick.planner": {
            "handlers": ["console", "file"],
            "level": log_level,
            "propagate": True,
        },
    },
}

logging.config.dictConfig(logging_config)


def get_config(platform, planner_model, finder_model):
    c = BaseConfig()
    prompts_config = c.get_prompts(platform, planner_model, finder_model)
    planner_model_config = c.get_config_for_platform(planner_model, "planner", platform)
    finder_model_config = c.get_config_for_platform(finder_model, "finder", platform)
    c.prompts = prompts_config
    c.function_declarations = c.get_function_declarations(platform)

    c.models = {
        "planner_config": planner_model_config,
        "finder_config": finder_model_config,
    }
    return c

from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)


class Planner(ABC):
    @abstractmethod
    def llm_response(self, prompt, screenshot) -> str:
        pass

    @abstractmethod
    def add_finder_message(self, message):
        pass

    @abstractmethod
    def task_finished(self, reason):
        pass

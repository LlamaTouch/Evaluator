from abc import ABC, abstractmethod
import os
from enum import Enum


class TaskCategory(Enum):
    GENERAL = "general"
    GOOGLEAPPS = "googleapps"
    INSTALL = "install"
    WEBSHOPPING = "webshopping"
    GENERATED = "generated"


class BaseEvaluator(ABC):
    def __init__(self, agent_name, agent_exec_trace_folder):
        self.agent_name = agent_name
        self.agent_exec_trace_folder = agent_exec_trace_folder
        self.evaluator_name = None

        self.epi_to_category_file = "data/epi_to_category.csv"
        assert os.path.exists(
            self.epi_to_category_file
        ), f"The file {self.epi_to_category_file} does not exist"

        self.epi_metadata_dict = {}
        self.init_epi_to_category()

    def init_epi_to_category(self):
        with open(self.epi_to_category_file, "r") as f:
            next(f)  # f is an iterable file object; skip the header
            for line in f:
                epi, category, task_description = line.strip().split(",", maxsplit=2)
                self.epi_metadata_dict[epi] = {
                    "category": category,
                    "task_description": task_description,
                }

    @abstractmethod
    def run_evaluation(self):
        pass

    @abstractmethod
    def report_stats(self):
        pass

    def query_task_decsription_by_episode(self, episode) -> str:
        return self.epi_metadata_dict[episode]["task_description"]

    def query_category_by_episode(self, episode) -> TaskCategory:
        return self.epi_metadata_dict[episode]["category"]

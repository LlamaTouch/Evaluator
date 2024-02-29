import logging
from abc import ABC, abstractmethod
import os
from task_trace import TaskCategory


class BaseEvaluator(ABC):
    # ------------------------------------------------------------------------ #
    # ------------------ Initialization ------------------ #
    # ------------------------------------------------------------------------ #
    def __init__(self, agent_name, agent_exec_trace_folder):
        # logger setup
        logging.basicConfig(level=logging.INFO)
        self.logger = None

        # agent metadata setup
        self.agent_name = agent_name
        self.agent_exec_trace_folder = agent_exec_trace_folder
        self.evaluator_name = None

        # load task metadata
        self.epi_to_category_file = "data/epi_to_category.csv"
        assert os.path.exists(
            self.epi_to_category_file
        ), f"The file {self.epi_to_category_file} does not exist"
        self.epi_metadata_dict = {}
        self.init_epi_to_category()

    def init_epi_to_category(self):
        """
        Load episode metadata from the file {self.epi_to_category_file}
        Format: {
            "episode": {
                "category": xx,
                "task_description": xx,
            },
            ...
        }
        """
        with open(self.epi_to_category_file, "r") as f:
            next(f)  # f is an iterable file object; skip the header
            for line in f:
                epi, category, task_description = line.strip().split(",", maxsplit=2)
                self.epi_metadata_dict[epi] = {
                    "category": category,
                    "task_description": task_description,
                }

    # ------------------------------------------------------------------------ #
    # ------------  Evaluation implementation ------------ #
    # ------------------------------------------------------------------------ #
    def run_evaluation(self):
        self.logger.info("Start evaluation")
        for epi in self.epi_metadata_dict.keys():
            self.eval_episode(epi)

    def eval_episode(self, episode):
        self.logger.info(f"Evaluating episode: {episode}")

    # ------------------------------------------------------------------------ #
    # -------------------  Metrics ----------------------- #
    # ------------------------------------------------------------------------ #
    @abstractmethod
    def report_stats(self):
        pass

    # ------------------------------------------------------------------------ #
    # ------------------ Helper functions ---------------- #
    # ------------------------------------------------------------------------ #
    def query_task_decsription_by_episode(self, episode) -> str:
        return self.epi_metadata_dict[episode]["task_description"]

    def query_category_by_episode(self, episode) -> TaskCategory:
        return self.epi_metadata_dict[episode]["category"]

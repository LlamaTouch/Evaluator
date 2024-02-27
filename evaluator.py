from abc import ABC, abstractmethod
import os


class BaseEvaluator(ABC):
    def __init__(self, agent_name, agent_exec_trace_folder):
        self.agent_name = agent_name
        self.agen_exec_trace_folder = agent_exec_trace_folder
        self.evaluator_name = None

        self.epi_to_category_file = "data/epi_to_category.csv"
        assert os.path.exists(
            self.epi_to_category_file
        ), f"The file {self.epi_to_category_file} does not exist"

        self.epi_to_category = {}
        self.init_epi_to_category()

    def init_epi_to_category(self):
        with open(self.epi_to_category_file, "r") as f:
            next(f)  # f is an iterable file object; skip the header
            for line in f:
                epi, category = line.strip().split(",")
                self.epi_to_category[epi] = category

    @abstractmethod
    def run_evaluation(self):
        pass

    @abstractmethod
    def report_stats(self):
        pass

    def query_category_by_episode(self, episode):
        return self.epi_to_category[episode]

import logging
from abc import ABC, abstractmethod
from typing import Dict
from task_trace import DatasetHelper


class BaseEvaluator(ABC):
    # ------------------------------------------------------------------------ #
    # ------------------ Initialization ------------------ #
    # ------------------------------------------------------------------------ #
    def __init__(self, agent_name):
        # logger setup
        logging.basicConfig(level=logging.INFO)
        self.logger = None

        # agent metadata setup
        self.agent_name = agent_name
        self.evaluator_name = None

        # helper instance
        self.helper = DatasetHelper()

    # ------------------------------------------------------------------------ #
    # ------------  Evaluation implementation ------------ #
    # ------------------------------------------------------------------------ #
    def run_evaluation(self):
        self.logger.info("Start evaluation")
        episode_completion: Dict[str, bool] = {}
        for epi in self.helper.get_all_episodes():
            completeness: bool = self.eval_episode(epi)
            episode_completion[epi] = completeness

    def eval_episode(self, episode) -> bool:
        self.logger.info(f"Evaluating episode: {episode}")
        task_description = self.helper.get_task_decsription_by_episode(episode)
        return self.eval_impl(episode, task_description)

    @abstractmethod
    def eval_impl(self, episode, task_description) -> bool:
        pass

    # ------------------------------------------------------------------------ #
    # -------------------  Metrics ----------------------- #
    # ------------------------------------------------------------------------ #
    @abstractmethod
    def report_stats(self):
        pass

import logging
from abc import ABC, abstractmethod
from typing import Dict

from agent import MobileAgent
from task_trace import Agent, DatasetHelper, TaskTrace


class BaseEvaluator(ABC):
    def __init__(self, agent: MobileAgent) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = None
        self.agent: MobileAgent = agent
        self.evaluator_name: str = None
        self.helper = DatasetHelper()
        self.episode_completion: Dict[str, bool] = {}

    def run_evaluation(self) -> None:
        self.logger.info("Start evaluation")
        for epi in self.helper.get_all_episodes():
            completeness: bool = self.eval_episode(epi)
            self.episode_completion[epi] = completeness

    def eval_episode(self, episode: str) -> bool:
        self.logger.info(f"Evaluating episode: {episode}")
        task_description = self.helper.get_task_decsription_by_episode(episode)
        return self.eval_impl(episode, task_description)

    @abstractmethod
    def eval_impl(self, episode: str, task_description: str) -> bool:
        pass

    def report_stats(self) -> None:
        num_true, num_false = 0, 0
        for v in self.episode_completion.values():
            if v:
                num_true += 1
            else:
                num_false += 1
        print(self.episode_completion)
        print(f"Number of True: {num_true}, Number of False: {num_false}")

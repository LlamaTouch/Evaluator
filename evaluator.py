import logging
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
from enum import Enum

from .agent import MobileAgent
from .task_trace import DatasetHelper


class FailedReason(Enum):
    EXEC_TRACE_NOT_FOUND = "execution trace not found"
    REF_TRACE_NOT_FOUND = "reference trace not found"
    STEP_CHECK_FAILED = "step checking failed"


class BaseEvaluator(ABC):
    def __init__(self, agent: MobileAgent) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = None
        self.agent: MobileAgent = agent
        self.evaluator_name: str = None
        self.helper = DatasetHelper()
        self.episode_completion: Dict[str, Tuple[bool, str]] = {}

    def run_evaluation(self) -> None:
        self.logger.info("Start evaluation")
        for epi in self.helper.get_all_episodes():
            completeness, failed_reason = self.eval_episode(epi)
            if failed_reason is not None:
                self.episode_completion[epi] = (completeness, failed_reason.value)
            else:
                self.episode_completion[epi] = (completeness, "")

    def eval_episode(self, episode: str) -> Tuple[bool, Optional[FailedReason]]:
        self.logger.info(f"Evaluating episode: {episode}")
        task_description = self.helper.get_task_decsription_by_episode(episode)
        return self.eval_impl(episode, task_description)

    @abstractmethod
    def eval_impl(
        self, episode: str, task_description: str
    ) -> Tuple[bool, Optional[FailedReason]]:
        pass

    def report_stats(self) -> None:
        num_true, num_false = 0, 0
        for v, _ in self.episode_completion.values():
            if v:
                num_true += 1
            else:
                num_false += 1
        print(f"Completed tasks: {num_true}, failed tasks: {num_false}")
        self.dump_stats()

    def dump_stats(self) -> None:
        stats = [
            f"{epi},{success},{reason}\n"
            for epi, (success, reason) in self.episode_completion.items()
        ]
        if not os.path.exists("dumped_stats"):
            os.mkdir("dumped_stats")
        # construct stats file using current time, evaluator name, and agent name
        # time format: {yyyy}-{mm}-{dd}-{hh}-{mm}-{ss}
        file_name = f"dumped_stats/{self.evaluator_name}_{self.agent.agent_name}_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.csv"
        with open(file_name, "w") as f:
            f.writelines(stats)
        print(f"Evaluation results were dumped to file {file_name}")

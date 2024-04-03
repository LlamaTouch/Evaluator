import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .agent import MobileAgent
from .task_trace import DatasetHelper


class FailedReason(Enum):
    GR_TRACE_NOT_FOUND = "ground-truth trace not found"
    EXEC_TRACE_NOT_FOUND = "execution trace not found"
    REF_TRACE_NOT_FOUND = "reference trace not found"
    STEP_CHECK_FAILED = "step checking failed"
    UI_POSITIONS_NOT_FOUND = "ui positions not found"


class BaseEvaluator(ABC):
    def __init__(self, agent: MobileAgent, options: Dict = None) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = None
        self.agent: MobileAgent = agent
        self.evaluator_name: str = None
        self.helper = DatasetHelper()
        self.episode_completion: Dict[str, Tuple[bool, str]] = {}
        # evaluation options: by default, all episodes will be evaluated
        #   - "categories": [TaskCategory.GENERAL, TaskCategory.GOOGLEAPPS, ...]
        #                 only evaluate episodes in target categories
        #   - "first_n": only evaluating the first_n episodes
        #   - "episodes": [episode_1, episode_2, ...]
        #                 only evaluate target episodes
        self.options = options if options else None

    def run_evaluation(self) -> None:
        target_episodes = self.helper.get_all_episodes()

        if self.options:
            if "categories" in self.options:
                target_episodes = [
                    epi
                    for category in self.options["categories"]
                    for epi in self.helper.get_episodes_by_category(category)
                ]
            elif "episodes" in self.options:
                target_episodes = self.options["episodes"]
            elif "first_n" in self.options:
                first_n = int(self.options["first_n"])
                target_episodes = self.helper.get_all_episodes()[:first_n]

        for epi in target_episodes:
            completeness, failed_reason = self.eval_episode(epi)
            if failed_reason is not None:
                # users may pass string or FailedReason enum as parameter
                # accept and record both of them
                failed_reason_str = (
                    failed_reason.value
                    if isinstance(failed_reason, FailedReason)
                    else failed_reason
                )
                self.episode_completion[epi] = (completeness, failed_reason_str)
            else:
                self.episode_completion[epi] = (completeness, "")

    def eval_episode(self, episode: str) -> Tuple[bool, Optional[FailedReason]]:
        self.logger.info(f"Evaluating episode: {episode}")
        task_description = self.helper.get_task_description_by_episode(episode)
        try:
            ret = self.eval_impl(episode, task_description)
        except Exception as e:
            self.logger.error(f"Failed to evaluate episode {episode}: {str(e)}")
            # TODO: add FailedReason for this case
            return False, FailedReason.UI_POSITIONS_NOT_FOUND
        return ret

    @abstractmethod
    def eval_impl(
        self, episode: str, task_description: str
    ) -> Tuple[bool, Optional[FailedReason]]:
        pass

    def report_stats(
        self,
        human_eval_path: str = None,
        only_human_eval_positive: bool = False,
        to_stdout: bool = False,
    ) -> None:
        exec_dict = {
            epi: completed for epi, (completed, _) in self.episode_completion.items()
        }
        exec_df = pd.DataFrame(exec_dict.items(), columns=["episode", "execution"])
        if not human_eval_path:
            exec_positive = (exec_df["execution"] == 1).sum()
            exec_negative = (exec_df["execution"] == 0).sum()
            print(f"Completed tasks: {exec_positive}, failed tasks: {exec_negative}")
            self._dump_stats(to_stdout=to_stdout)
        else:
            with open(human_eval_path, "r") as f:
                human_df = pd.read_csv(f)
            eval_df = human_df.merge(exec_df, on="episode", how="inner")
            if only_human_eval_positive:
                eval_df = eval_df[eval_df[eval_df.columns[1]] == 1]
            total = eval_df.shape[0]
            if only_human_eval_positive and total < 1:
                total = 1

            human_positive = (eval_df[eval_df.columns[1]] == 1).sum()
            exec_positive = (exec_df["execution"] == 1).sum()
            exec_negative = total - exec_positive
            print(f"Completed tasks: {exec_positive}, failed tasks: {exec_negative}")
            tp = (eval_df[eval_df.columns[1]] == eval_df["execution"]).sum()
            self._dump_stats(metric=(total, human_positive, exec_positive, tp), to_stdout=to_stdout)

    def _dump_stats(
        self, metric: Tuple[int, int, int, int] = None, to_stdout: bool = False
    ) -> None:
        total, human_positive, exec_positive, tp = metric
        human_tcr = human_positive / total
        tcr = exec_positive / total
        acc = tp / total

        stats = [
            f"{epi},{success},{reason}\n"
            for epi, (success, reason) in self.episode_completion.items()
        ]

        if to_stdout:
            print("".join(stats))
            exit(0)

        if metric:
            stats.append(f"total tasks = {total}, human positive = {human_positive}, agent positive = {exec_positive}, true positive = {tp}\n")
            stats.append(f"human task completion rate: {human_tcr}\n")
            stats.append(f"end-to-end task completion rate: {tcr}\n")
            stats.append(f"accuracy: {acc}\n")

        if not os.path.exists("dumped_stats"):
            os.mkdir("dumped_stats")
        # construct stats file using current time, evaluator name, and agent name
        # time format: {yyyy}-{mm}-{dd}-{hh}-{mm}-{ss}
        file_name = f"dumped_stats/{self.evaluator_name}_{self.agent.agent_name}_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.csv"
        with open(file_name, "w") as f:
            f.writelines(stats)
        print(f"Evaluation results were dumped to file {file_name}")

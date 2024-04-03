import os
import pickle
from typing import Optional, Dict, List

import pandas as pd

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.lcsmatch_evaluator import LCSMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator

APPAGENT_EXEC_TRACE_PATH = os.getenv(
    "APPAGENT_EXEC_TRACE_PATH", "/data/wangshihe/AgentTestbed/AgentEnvTestbed/AppAgent"
)


class AppAgent(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.APPAGENT
        self.appagent_category_to_trace_folder_name = {
            TaskCategory.GENERAL: "tasks-240214-1-general",
            TaskCategory.GOOGLEAPPS: "tasks-240216-1-googleapp",
            TaskCategory.INSTALL: "tasks-240215-2-install",
            TaskCategory.WEBSHOPPING: "tasks-240215-1-webshopping",
            TaskCategory.GENERATED: "tasks-240403-1-generated-all",
        }
        self.epi_to_trace_path: Dict[str, str] = {}
        self.epi_to_exec_trace_path: Dict[str, str] = {}

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        if not self.epi_to_exec_trace_path:
            self._proc_all_exec_trace()

        try:
            epi_trace_path = self.epi_to_exec_trace_path[episode]
            trace = DatasetHelper().load_testbed_trace_by_path(epi_trace_path)
        except KeyError as e:
            return None
        act_list: List[Action] = [item.action for item in trace]
        return act_list

    def _proc_all_exec_trace(self) -> None:
        """exec trace on testbed"""
        for k, v in self.appagent_category_to_trace_folder_name.items():
            if v is None:
                continue
            summary_csv = os.path.join(
                APPAGENT_EXEC_TRACE_PATH, v, "appagent_trace.csv"
            )
            data = pd.read_csv(summary_csv)
            for _, row in data.iterrows():
                folder_name = row["trace_folder_path"].split("/")[-1]
                epi = str(row["episode_id"])
                self.epi_to_exec_trace_path[epi] = os.path.join(
                    APPAGENT_EXEC_TRACE_PATH, v, folder_name, epi, "captured_data"
                )

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        if not self.epi_to_exec_trace_path:
            self._proc_all_exec_trace()
        epi_trace_path = self.epi_to_exec_trace_path[episode]
        return DatasetHelper().load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        if not self.epi_to_exec_trace_path:
            self._proc_all_exec_trace()
        return self.epi_to_exec_trace_path[episode]


if __name__ == "__main__":
    table_all_successful_FLAG = False
    human_eval_path = "/data/wangshihe/AgentTestbed/Evaluator/appagent_human_eval.csv"
    agent = AppAgent()

    e = ExactMatchEvaluator(
        agent=agent,
        options={
            "categories": [
                TaskCategory.GENERAL,
                TaskCategory.GOOGLEAPPS,
                TaskCategory.INSTALL,
                TaskCategory.WEBSHOPPING,
                TaskCategory.GENERATED,
            ]
        },
    )
    e.run_evaluation()
    e.report_stats(
        human_eval_path=human_eval_path,
        only_human_eval_positive=table_all_successful_FLAG,
    )

    l = LCSMatchEvaluator(
        agent=agent,
        options={
            "categories": [
                TaskCategory.GENERAL,
                TaskCategory.GOOGLEAPPS,
                TaskCategory.INSTALL,
                TaskCategory.WEBSHOPPING,
                TaskCategory.GENERATED,
            ]
        },
    )
    l.run_evaluation()
    l.report_stats(
        human_eval_path=human_eval_path,
        only_human_eval_positive=table_all_successful_FLAG,
    )

    t = TestbedEvaluator(
        agent=agent,
        options={
            "categories": [
                TaskCategory.GENERAL,
                TaskCategory.GOOGLEAPPS,
                TaskCategory.INSTALL,
                TaskCategory.WEBSHOPPING,
                TaskCategory.GENERATED,
            ]
        },
    )
    t.run_evaluation()
    t.report_stats(
        human_eval_path=human_eval_path,
        only_human_eval_positive=table_all_successful_FLAG,
    )

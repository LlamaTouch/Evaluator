import os
from typing import Dict, List, Optional

import pandas as pd

from config import CONFIG
from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.lcsmatch_evaluator import LCSMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator

APPAGENT_EXEC_TRACE_PATH = os.getenv(
    "APPAGENT_EXEC_TRACE_PATH", CONFIG.APPAGENT_EXEC_TRACE_PATH
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
        self.helper = DatasetHelper(CONFIG.EPI_METADATA_PATH)

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        if not self.epi_to_exec_trace_path:
            self._proc_all_exec_trace()

        if episode not in self.epi_to_exec_trace_path:
            return None
        epi_trace_path = self.epi_to_exec_trace_path[episode]
        trace = self.helper.load_testbed_trace_by_path(epi_trace_path)
        act_list: List[Action] = [
            item.action for item in trace if item.action is not None
        ]
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

        if episode not in self.epi_to_exec_trace_path:
            return None
        epi_trace_path = self.epi_to_exec_trace_path[episode]
        return self.helper.load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        if not self.epi_to_exec_trace_path:
            self._proc_all_exec_trace()
        return self.epi_to_exec_trace_path[episode]


if __name__ == "__main__":
    human_eval_path = CONFIG.APPAGENT_HUMANEVAL_PATH
    table_all_successful_FLAG = False
    suffix = "only_human_success"
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
        suffix=suffix,
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
        suffix=suffix,
    )

    options_base = {
        "categories": [
            TaskCategory.GENERAL,
            TaskCategory.GOOGLEAPPS,
            TaskCategory.INSTALL,
            TaskCategory.WEBSHOPPING,
            TaskCategory.GENERATED,
        ]
    }
    ablation_list = [
        {
            "fuzzy_match": False,
            "exact_match": True,
            "screen_level_fuzzy_match": True,
        },
        {
            "fuzzy_match": False,
            "exact_match": True,
            "textbox_fuzzy_match": True,
        },
        {
            "fuzzy_match": True,
            "exact_match": False,
            "activity_exact_match": True,
            "action_exact_match": False,
            "UI_component_exact_match": False,
            "system_state_exact_match": False,
        },
        {
            "fuzzy_match": True,
            "exact_match": False,
            "activity_exact_match": False,
            "action_exact_match": True,
            "UI_component_exact_match": False,
            "system_state_exact_match": False,
        },
        {
            "fuzzy_match": True,
            "exact_match": False,
            "activity_exact_match": False,
            "action_exact_match": False,
            "UI_component_exact_match": True,
            "system_state_exact_match": False,
        },
        {
            "fuzzy_match": True,
            "exact_match": False,
            "activity_exact_match": False,
            "action_exact_match": False,
            "UI_component_exact_match": False,
            "system_state_exact_match": True,
        },
    ]

    for idx, ablation in enumerate(ablation_list):
        t = TestbedEvaluator(
            agent=agent,
            options={**options_base, **ablation},
        )
        t.run_evaluation()
        t.report_stats(
            human_eval_path=human_eval_path,
            only_human_eval_positive=table_all_successful_FLAG,
            suffix=f"{idx}_th_ablation",
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
        suffix=suffix,
    )

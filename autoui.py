import argparse
import os
from typing import List, Optional

from config import CONFIG
from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.lcsmatch_evaluator import LCSMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator


class AutoUI(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTOUI
        self.agent_exec_trace_path = CONFIG.AUTOUI_EXEC_TRACE_PATH

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        exec_trace: TaskTrace = self.load_exec_trace_by_episode(episode)
        if exec_trace:
            return [ui_state.action for ui_state in exec_trace]
        return None

    def load_exec_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        helper = DatasetHelper(CONFIG.EPI_METADATA_PATH, CONFIG.GR_DATASET_PATH)
        category = helper.get_category_by_episode(episode)
        if category == TaskCategory.WEBSHOPPING:
            category_val = "web_shopping"
        elif category == TaskCategory.GOOGLEAPPS:
            category_val = "google_apps"
        else:
            category_val = category.value
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category_val, episode, "captured_data"
        )
        if not os.path.exists(epi_trace_path):
            return None
        return helper.load_testbed_trace_by_path(epi_trace_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AutoUI evaluation.")
    parser.add_argument(
        "--eval", type=str, help='Evaluation type: "testbed (t)" or "exact (e)"'
    )
    args = parser.parse_args()

    agent = AutoUI()

    if args.eval == "exact" or args.eval == "e":
        e = ExactMatchEvaluator(
            agent=agent,
            epi_metadata_path=CONFIG.EPI_METADATA_PATH,
            gr_dataset_path=CONFIG.GR_DATASET_PATH,
            options={
                "categories": [
                    TaskCategory.GENERAL,
                    TaskCategory.GOOGLEAPPS,
                    TaskCategory.INSTALL,
                    TaskCategory.WEBSHOPPING,
                    TaskCategory.GENERATED,
                ],
            },
        )
        e.run_evaluation()
        e.report_stats(
            human_eval_path=CONFIG.AUTOUI_HUMANEVAL_PATH,
            only_human_eval_positive=False,
            suffix="only_human_success",
        )

    elif args.eval == "testbed" or args.eval == "t":
        t = TestbedEvaluator(
            agent=agent,
            epi_metadata_path=CONFIG.EPI_METADATA_PATH,
            gr_dataset_path=CONFIG.GR_DATASET_PATH,
            options={
                "categories": [
                    TaskCategory.GENERAL,
                    TaskCategory.GOOGLEAPPS,
                    TaskCategory.INSTALL,
                    TaskCategory.WEBSHOPPING,
                    TaskCategory.GENERATED,
                ],
                "check_fuzzy_match": True,
                "check_exact_match": True,
                "check_system_state": True,
            },
        )
        t.run_evaluation()
        t.report_stats(
            human_eval_path=CONFIG.AUTOUI_HUMANEVAL_PATH,
            only_human_eval_positive=False,
            suffix="only_human_success",
        )
    elif args.eval == "lcs-exact" or args.eval == "lcse":
        t = LCSMatchEvaluator(
            agent=agent,
            epi_metadata_path=CONFIG.EPI_METADATA_PATH,
            gr_dataset_path=CONFIG.GR_DATASET_PATH,
            options={
                "categories": [
                    TaskCategory.GENERAL,
                    TaskCategory.GOOGLEAPPS,
                    TaskCategory.INSTALL,
                    TaskCategory.WEBSHOPPING,
                    TaskCategory.GENERATED,
                ],
            },
        )
        t.run_evaluation()
        t.report_stats(
            human_eval_path=CONFIG.AUTOUI_HUMANEVAL_PATH,
            only_human_eval_positive=False,
            suffix="only_human_success",
        )
    else:
        raise Exception(
            f"Invalid evaluation type: {args.eval}, expected: testbed/t and exact/e"
        )

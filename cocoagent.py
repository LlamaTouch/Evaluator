import argparse
import os
from typing import Dict, List, Optional

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.lcsmatch_evaluator import LCSMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator


class CoCoAgent(MobileAgent):

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.COCOAGENT
        self.epi_to_exec_trace_path = {}
        self.base_folder = (
            "/data/zzh/mobile-agent/CoCoAgent/agentenv/agent_result/all_data"
        )

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        exec_trace: TaskTrace = self.load_exec_trace_by_episode(episode)
        if exec_trace:
            return [ui_state.action for ui_state in exec_trace]
        return None

    def load_exec_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        epi_folder = os.path.join(self.base_folder, episode)
        if not os.path.exists(epi_folder):
            return None

        return DatasetHelper().load_testbed_trace_by_path(epi_folder)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CoCo-Agent evaluation.")
    parser.add_argument(
        "--eval", type=str, help='Evaluation type: "testbed (t)" or "exact (e)"'
    )
    args = parser.parse_args()

    agent = CoCoAgent()

    if args.eval == "exact" or args.eval == "e":
        e = ExactMatchEvaluator(
            agent=agent,
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
        e.report_stats()

    elif args.eval == "testbed" or args.eval == "t":
        t = TestbedEvaluator(
            agent=agent,
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
        t.report_stats()

    elif args.eval == "lcs-exact" or args.eval == "lcse":
        t = LCSMatchEvaluator(
            agent=agent,
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
        t.report_stats()

    else:
        raise Exception(
            f"Invalid evaluation type: {args.eval}, expected: testbed/t and exact/e"
        )
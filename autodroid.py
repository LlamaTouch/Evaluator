import argparse
import os
from typing import Dict, List, Optional

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator


class AutoDroid(MobileAgent):

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTODROID
        self.epi_to_exec_trace_path = {}
        self.base_folder = "/home/zl/mobile-agent/testbed/AutoDroid/exec_output"

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        exec_trace: TaskTrace = self.load_exec_trace_by_episode(episode)
        if exec_trace:
            return [ui_state.action for ui_state in exec_trace]
        return None

    
    # def load_predicted_action_by_episode(self, episode: str) -> List[Action]:
    #     """Predicted actions on dataset.
    #     If there is no corresponding action file, return an empty list"""
    #     base_folder = "/home/zl/mobile-agent/testbed/AutoDroid/predicted_actions/"
    #     # build the map between episode and path
    #     epis = [f.split(".")[0] for f in os.listdir(base_folder)]

    #     if episode not in epis:
    #         return []

    #     epi_file = os.path.join(base_folder, f"{episode}.json")
    #     with open(epi_file) as f:
    #         data = json.load(f)
    #     act_list: List[Action] = []
    #     for _, v in data.items():
    #         action_type = v["event_type"]  # BACK, CLICK, SET_TEXT
    #         action_param = v["param"]
    #         screen_height = v["screen_height"]
    #         screen_width = v["screen_width"]

    #         print(action_param, type(action_param))

    #         if action_type == "BACK":
    #             act = Action(action_type=ActionType.PRESS_BACK)
    #         elif action_type == "CLICK":
    #             act = Action(
    #                 action_type=ActionType.DUAL_POINT,
    #                 touch_point_yx=(
    #                     action_param[1] / screen_height,
    #                     action_param[0] / screen_width,
    #                 ),
    #                 lift_point_yx=(
    #                     action_param[1] / screen_height,
    #                     action_param[0] / screen_width,
    #                 ),
    #             )
    #         elif action_type == "SET_TEXT":
    #             act = Action(
    #                 action_type=ActionType.TYPE,
    #                 typed_text=action_param,
    #             )

    #         act_list.append(act)
    #     return act_list

    def proc_all_exec_trace(self) -> None:
        """exec trace on testbed"""
        pass

    def load_exec_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        epi_folder = os.path.join(self.base_folder, episode)
        if not os.path.exists(epi_folder):
            return None

        return DatasetHelper().load_testbed_trace_by_path(epi_folder)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AutoUI evaluation.")
    parser.add_argument(
        "--eval", type=str, help='Evaluation type: "testbed (t)" or "exact (e)"'
    )
    args = parser.parse_args()

    agent = AutoDroid()

    if args.eval == "exact" or args.eval == "e":
        e = ExactMatchEvaluator(agent=agent)
        e.run_evaluation()
        e.report_stats(to_stdout=True)

    elif args.eval == "testbed" or args.eval == "t":
        t = TestbedEvaluator(
            agent=agent,
            options={
                "check_fuzzy_match": True,
                "check_exact_match": True,
                "check_system_state": True,
            },
        )
        t.run_evaluation()
        t.report_stats(to_stdout=True)
    else:
        raise Exception(
            f"Invalid evaluation type: {args.eval}, expected: testbed/t and exact/e"
        )


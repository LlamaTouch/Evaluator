import json
import os
import pickle
from typing import Dict, List

import pandas as pd

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace


class AutoDroid(MobileAgent):

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTODROID
        self.epi_to_exec_trace_path = {}

    def load_predicted_action_by_episode(self, episode: str) -> List[Action]:
        """Predicted actions on dataset.
        If there is no corresponding action file, return an empty list"""
        base_folder = "/home/zl/mobile-agent/testbed/AutoDroid/predicted_actions/"
        # build the map between episode and path
        epis = [f.split(".")[0] for f in os.listdir(base_folder)]

        if episode not in epis:
            return []

        epi_file = os.path.join(base_folder, f"{episode}.json")
        with open(epi_file) as f:
            data = json.load(f)
        act_list: List[Action] = []
        for _, v in data.items():
            action_type = v["event_type"]  # BACK, CLICK, SET_TEXT
            action_param = v["param"]
            screen_height = v["screen_height"]
            screen_width = v["screen_width"]

            print(action_param, type(action_param))

            if action_type == "BACK":
                act = Action(action_type=ActionType.PRESS_BACK)
            elif action_type == "CLICK":
                act = Action(
                    action_type=ActionType.DUAL_POINT,
                    touch_point_yx=(
                        action_param[1] / screen_height,
                        action_param[0] / screen_width,
                    ),
                    lift_point_yx=(
                        action_param[1] / screen_height,
                        action_param[0] / screen_width,
                    ),
                )
            elif action_type == "SET_TEXT":
                act = Action(
                    action_type=ActionType.TYPE,
                    typed_text=action_param,
                )

            act_list.append(act)
        return act_list

    def proc_all_exec_trace(self) -> None:
        """exec trace on testbed"""
        pass

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        pass

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        pass


if __name__ == "__main__":
    agent = AutoDroid()
    e = ExactMatchEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()

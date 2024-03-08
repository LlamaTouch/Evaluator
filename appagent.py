import os
import pickle
from typing import Dict, List

import pandas as pd

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace


class AppAgent(MobileAgent):

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.APPAGENT
        self.epi_to_exec_trace_path = {}

    def load_predicted_action_by_episode(self, episode: str) -> List[Action]:
        """Predicted actions on dataset.
        If there is no corresponding action file, return an empty list"""
        base_folder = "/data/wangshihe/AgentTestbed/Evaluator/AppAgent/tasks-240306-all"
        # build the map between episode and path
        epi_to_trace_path = {}
        for folder in os.listdir(base_folder):
            trace_folder = os.path.join(base_folder, folder)
            episode_anno_file = os.path.join(trace_folder, "task_metadata.txt")
            if not os.path.exists(episode_anno_file):
                continue
            with open(episode_anno_file, "r") as f:
                epi = eval(f.read())["epi"]
            epi_to_trace_path[epi] = trace_folder

        if episode not in epi_to_trace_path.keys():
            return []

        trace_path = epi_to_trace_path[episode]
        predicted_action_file = os.path.join(trace_path, "appagent_action.obj")
        if not os.path.exists(predicted_action_file):
            return []
        with open(os.path.join(trace_path, "appagent_action.obj"), "rb") as f:
            """actions: [
                {
                    "action_type": ActionType,
                    "touch_point": [y, x],
                    "lift_point": [y, x],
                    "typed_text": "text",
                },
                ...
            ]"""
            actions = pickle.load(f)
        # convert evnery action in actions to Action
        act_list: List[Action] = []
        for action in actions:
            # WARNING: deprecated feature used
            if isinstance(action["action_type"], type):
                action["action_type"] = "type"

            act = Action(
                action_type=ActionType[action["action_type"].upper()],
                touch_point_yx=tuple(action["touch_point"]),
                lift_point_yx=tuple(action["lift_point"]),
                typed_text=action["typed_text"],
            )
            act_list.append(act)
        return act_list

    def proc_all_exec_trace(self) -> None:
        """exec trace on testbed"""
        base_folder = "/data/wangshihe/AgentTestbed/AppAgent"
        appagent_category_to_trace_folder_name = {
            TaskCategory.GENERAL: "tasks-240214-1-general",
            TaskCategory.GOOGLEAPPS: "tasks-240216-1-googleapp",
            TaskCategory.INSTALL: "tasks-240215-2-install",
            TaskCategory.WEBSHOPPING: "tasks-240215-1-webshopping",
            TaskCategory.GENERATED: None,
        }
        for k, v in appagent_category_to_trace_folder_name.items():
            if v is None:
                continue
            summary_csv = os.path.join(base_folder, v, "appagent_trace.csv")
            data = pd.read_csv(summary_csv)
            for _, row in data.iterrows():
                folder_name = row["trace_folder_path"].split("/")[-1]
                epi = str(row["episode_id"])
                self.epi_to_exec_trace_path[epi] = os.path.join(
                    base_folder, v, folder_name, epi, "captured_data"
                )

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        if not self.epi_to_exec_trace_path:
            self.proc_all_exec_trace()
            # print(f"Reading {len(self.epi_to_trace_path)} episodes in total")
        epi_trace_path = self.epi_to_exec_trace_path[episode]
        return DatasetHelper().load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        if not self.epi_to_exec_trace_path:
            self.proc_all_exec_trace()
            print(f"Reading {len(self.epi_to_trace_path)} episodes in total")
        return self.epi_to_exec_trace_path[episode]


if __name__ == "__main__":
    agent = AppAgent()
    e = ExactMatchEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()
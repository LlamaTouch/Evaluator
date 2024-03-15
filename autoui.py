import ast
import json
import os
import pickle
from typing import Dict, List

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace
from evaluator.testbed_evaluator import TestbedEvaluator


class AutoUI(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTOUI
        self.agent_exec_trace_path = (
            "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result"
        )
        self.epi_to_action_list: Dict[str, List[Action]] = {}

    def load_predicted_action_by_episode(self, episode: str) -> List[Action]:
        # check if the action list is already loaded
        if episode in self.epi_to_action_list.keys():
            return self.epi_to_action_list[episode]

        eval_result_file = "/data/zzh/mobile-agent/Auto-UI/Evaluator/result/auto_ui_evaluator_last_screen.json"
        with open(eval_result_file) as f:
            data = json.load(f)

        for epi_data in data:
            act_list: List[Action] = []
            for action in epi_data["actions"]:
                act = Action(
                    action_type=ActionType[action["action_type"].upper()],
                    touch_point_yx=tuple(ast.literal_eval(action["touch_point"])),
                    lift_point_yx=tuple(ast.literal_eval(action["lift_point"])),
                    typed_text=action["typed_text"],
                )
                act_list.append(act)
            self.epi_to_action_list[epi_data["episode_id"]] = act_list

        return self.epi_to_action_list[episode]

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        category = DatasetHelper().get_category_by_episode(episode)
        if category == TaskCategory.WEBSHOPPING:
            category_val = "web_shopping"
        elif category == TaskCategory.GOOGLEAPPS:
            category_val = "google_apps"
        else:
            category_val = category.value
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category_val, episode, "captured_data"
        )
        return DatasetHelper().load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        # category = DatasetHelper().get_category_by_episode(episode)
        # epi_trace_path = os.path.join(
        #     self.agent_exec_trace_path, category.value, episode, "captured_data"
        # )
        # return epi_trace_path
        pass


if __name__ == "__main__":
    agent = AutoUI()
    e = ExactMatchEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()

    # t = TestbedEvaluator(
    #     agent=agent,
    #     options={
    #         # "episodes": ['10774240587109527791'],
    #         # "first_n": 30,
    #         "categories": [
    #             TaskCategory.GENERAL,
    #             TaskCategory.GOOGLEAPPS,
    #             TaskCategory.INSTALL,
    #             TaskCategory.WEBSHOPPING,
    #         ]
    #     },
    # )
    # t.run_evaluation()
    # t.report_stats()

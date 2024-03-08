import ast
import os
import pickle
from typing import Dict, List

from evaluator.agent import MobileAgent
from evaluator.common.action_type import Action, ActionType
from evaluator.exactmatch_evaluator import ExactMatchEvaluator
from evaluator.task_trace import Agent, DatasetHelper, TaskTrace
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

        eval_serialized_file = (
            "/data/zzh/mobile-agent/Auto-UI/Evaluator/result/auto_ui_evaluator.obj"
        )
        with open(eval_serialized_file, "rb") as f:
            eval_results: List[Dict] = pickle.load(f)
        for item in eval_results:
            epi = item["episode_id"]
            act_list: List[Action] = []
            for action in item["actions"]:
                act = Action(
                    action_type=ActionType[action["action_type"].upper()],
                    touch_point_yx=tuple(ast.literal_eval(action["touch_point"])),
                    lift_point_yx=tuple(ast.literal_eval(action["lift_point"])),
                    typed_text=action["typed_text"],
                )
                act_list.append(act)
            self.epi_to_action_list[epi] = act_list
        return self.epi_to_action_list[epi]

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        category = DatasetHelper().get_category_by_episode(episode)
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category.value, episode, "captured_data"
        )
        return DatasetHelper().load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        category = DatasetHelper().get_category_by_episode(episode)
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category.value, episode, "captured_data"
        )
        return epi_trace_path


if __name__ == "__main__":
    agent = AutoUI()
    # e = ExactMatchEvaluator(agent=agent)
    # e.run_evaluation()
    # e.report_stats()

    t = TestbedEvaluator(agent=agent)
    t.run_evaluation()
    t.report_stats()
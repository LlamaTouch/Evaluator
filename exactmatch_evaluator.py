import logging
import random

from agent import AppAgent
from evaluator import BaseEvaluator
from task_trace import load_groundtruth_trace_by_episode
from action_matching_impl import check_actions_match


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def eval_impl(self, episode, task_description) -> bool:
        groundtruth_trace = load_groundtruth_trace_by_episode(episode)
        agent_predicted_actions = self.agent.load_predicted_action_by_episode(episode)
        if len(agent_predicted_actions) == 0:
            return False
        print(len(agent_predicted_actions))
        ui_position_list = self.agent.load_episode_ui_positions(episode)
        for i, item in enumerate(groundtruth_trace):
            _, _, gr_action = item
            real_action = agent_predicted_actions[i]
            print(f"step{i}, {gr_action}")
            print(f"step{i}, {real_action}")
            ui_positions = ui_position_list[i]
            if not self.check_action_match_like_AITW(
                gr_action, real_action, ui_positions
            ):
                return False
            print(f"step{i} passed")
        return True

    def load_ui_positions(self, episode, index):
        """This info is required in the evaluation process"""
        pass

    def check_action_match_like_AITW(
        self, gr_action, exec_action, ui_positions
    ) -> bool:
        try:
            check_match = check_actions_match(
                gr_action.touch_point_yx,
                gr_action.lift_point_yx,
                gr_action.action_type,
                exec_action.touch_point_yx,
                exec_action.lift_point_yx,
                exec_action.action_type,
                ui_positions,
            )
        except Exception as e:
            check_match = False
        return check_match


if __name__ == "__main__":
    agent = AppAgent()
    e = ExactMatchEvaluator(agent=agent)
    ret = e.eval_episode("13563225379366283319")
    # e.run_evaluation()
    # e.report_stats()

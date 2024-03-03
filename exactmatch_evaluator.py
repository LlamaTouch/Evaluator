import logging
from typing import Tuple, Optional

from agent import AppAgent
from evaluator import BaseEvaluator, FailedReason
from action_matching_impl import check_actions_match


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        """Exact match evaluation using self-defined trace"""
        # option 1: use our annotated trace
        # gr_trace = self.helper.load_groundtruth_trace_by_episode(episode)
        # gr_actions = [ui_state[2] for ui_state in gr_trace]
        # option 2: use AITW trace
        gr_actions = self.agent.load_AITW_episode_actions(episode)
        if len(gr_actions) == 0:
            return False, FailedReason.REF_TRACE_NOT_FOUND

        agent_predicted_actions = self.agent.load_predicted_action_by_episode(episode)
        if len(agent_predicted_actions) == 0:
            return False, FailedReason.EXEC_TRACE_NOT_FOUND
        ui_position_list = self.agent.load_AITW_episode_ui_positions(episode)
        for i, gr_action in enumerate(gr_actions):
            real_action = agent_predicted_actions[i]
            print(f"step{i}, {gr_action}")
            print(f"step{i}, {real_action}")
            ui_positions = ui_position_list[i]
            if not self.check_action_match_like_AITW(
                gr_action, real_action, ui_positions
            ):
                return False, FailedReason.STEP_CHECK_FAILED
            print(f"step{i} passed")
        return True, None

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
    e.run_evaluation()
    e.report_stats()

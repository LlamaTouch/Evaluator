import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image

from .evaluator import BaseEvaluator, FailedReason
from .exactmatch_evaluation.action_matching import check_actions_match
from .utils.vh_simplify import extract_ui_positions_from_vh


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        """Exact match evaluation using self-defined trace"""
        gr_trace = self.helper.load_groundtruth_trace_by_episode(episode)
        screenshot_paths, vh_paths, gr_actions = zip(*gr_trace)
        agent_predicted_actions = self.agent.load_predicted_action_by_episode(episode)
        if len(agent_predicted_actions) == 0:
            return False, FailedReason.EXEC_TRACE_NOT_FOUND
        for i, gr_action in enumerate(gr_actions):
            real_action = agent_predicted_actions[i]
            ui_positions = self.extract_ui_positions_from_vh(
                screenshot_paths[i], vh_paths[i]
            )
            # print(f"step{i}, {gr_action}")
            # print(f"step{i}, {real_action}")
            # print(f"step{i}, {ui_positions}")
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

    def extract_ui_positions_from_vh(
        self, screenshot_path: str, vh_path: str
    ) -> np.ndarray[np.ndarray]:
        """Extract UI positions used for evaluation from view hierarchy

        Return:
            normalized_ui_positions: [
                [y, x, height, width],
                [y, x, height, width],
                [y, x, height, width],
                ...
            ]
        """
        screen_width, screen_height = Image.open(screenshot_path).size
        ui_positions = extract_ui_positions_from_vh(vh_path).astype(float)
        print(f"extracting {len(ui_positions)} UI positions from {vh_path}")
        if len(ui_positions) == 0:
            return np.array([])
        # normalize every single np.ndarray in ui_positions according to w, h
        ui_positions[:, [0, 2]] /= screen_height
        ui_positions[:, [1, 3]] /= screen_width
        return ui_positions
